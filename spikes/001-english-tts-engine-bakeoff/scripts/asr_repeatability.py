#!/usr/bin/env python3
import difflib
import json
import re
from pathlib import Path
from typing import Any

from runtime_provenance import (
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)

SPIKE = Path(__file__).resolve().parents[1]
REPO = SPIKE.parents[1]
PROFILE = json.loads(
    (
        REPO
        / "data"
        / "narrator-voices"
        / "natural_talker_male_qwen_blog"
        / "profile.json"
    ).read_text()
)
CORPUS = json.loads((SPIKE / "corpus.json").read_text())["samples"]
EXPECTED = " ".join(item["text"] for item in CORPUS)
ORDER = [item["id"] for item in CORPUS]
RUN_IDS = ["run_a", "run_b"]
WORK = SPIKE / "work"


def normalize(text: str) -> str:
    text = text.lower().replace("—", " ").replace("-", " ")
    return " ".join(re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text))


def lcs_word_recall(expected_tokens: list[str], actual_tokens: list[str]) -> float:
    if not expected_tokens:
        return 1.0
    previous = [0] * (len(actual_tokens) + 1)
    for expected in expected_tokens:
        current = [0]
        for index, actual in enumerate(actual_tokens, start=1):
            if expected == actual:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1] / len(expected_tokens)


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("profile_id") != PROFILE["id"]:
        raise RuntimeError("Repeatability manifest uses a different profile")
    if manifest.get("all_checks_passed") is not True:
        raise RuntimeError("Repeatability manifest all_checks_passed is not true")
    if manifest.get("failures") != []:
        raise RuntimeError("Repeatability manifest contains failures")
    if manifest.get("system_fingerprints") != PROFILE["runtime"]["repeatability_fingerprints"]:
        raise RuntimeError("Repeatability manifest system fingerprints mismatch")

    comparisons = manifest.get("cross_process_comparisons")
    if not isinstance(comparisons, list) or [
        item.get("sample_id") for item in comparisons if isinstance(item, dict)
    ] != ORDER:
        raise RuntimeError("Repeatability manifest comparison corpus/order mismatch")
    for comparison in comparisons:
        if not isinstance(comparison, dict) or not (
            comparison.get("raw_hash_equal") is True
            and comparison.get("normalized_hash_equal") is True
        ):
            raise RuntimeError("Repeatability manifest comparison did not succeed")

    auditions = manifest.get("auditions")
    if not isinstance(auditions, list) or [
        item.get("run_id") for item in auditions if isinstance(item, dict)
    ] != RUN_IDS:
        raise RuntimeError("Repeatability manifest audition run/order mismatch")
    work_root = WORK.resolve()
    for audition in auditions:
        file_value = audition.get("file")
        if not isinstance(file_value, str):
            raise RuntimeError("Repeatability manifest audition path missing")
        path = WORK / file_value
        if not path.resolve().is_relative_to(work_root) or not path.is_file():
            raise RuntimeError("Repeatability manifest audition path is unsafe or missing")
        if audition.get("sample_order") != ORDER:
            raise RuntimeError("Repeatability manifest audition corpus/order mismatch")
        if audition.get("sha256") != sha256(path):
            raise RuntimeError("Repeatability manifest audition hash mismatch")
    return auditions


def main() -> None:
    manifest = json.loads((WORK / "repeatability_manifest.json").read_text())
    if not isinstance(manifest, dict):
        raise RuntimeError("Repeatability manifest is not an object")
    auditions = validate_manifest(manifest)
    environment = verify_environment(PROFILE, SPIKE, "asr")
    fingerprints = verify_system_fingerprints(PROFILE)
    model_spec = PROFILE["verification"]["reference_asr"]["model"]
    snapshot, model_resolution = verified_model_snapshot(model_spec)

    import mlx_whisper

    expected = normalize(EXPECTED)
    expected_tokens = expected.split()
    records = []
    failures = []
    for audition in auditions:
        path = WORK / audition["file"]
        result = mlx_whisper.transcribe(
            str(path),
            path_or_hf_repo=str(snapshot),
            language="en",
            word_timestamps=False,
            verbose=False,
        )
        transcript = str(result["text"]).strip()
        actual = normalize(transcript)
        ratio = difflib.SequenceMatcher(None, expected, actual).ratio()
        recall = lcs_word_recall(expected_tokens, actual.split())
        passed = ratio >= 0.90 and recall >= 0.90
        record = {
            "run_id": audition["run_id"],
            "file": audition["file"],
            "transcript": transcript,
            "sequence_ratio": round(ratio, 4),
            "lcs_word_recall": round(recall, 4),
            "passed": passed,
        }
        records.append(record)
        if not passed:
            failures.append(record)
    output = {
        "profile_id": PROFILE["id"],
        "model": model_spec,
        "model_resolution": model_resolution,
        "runtime_environment": environment,
        "system_fingerprints": fingerprints,
        "thresholds": {"sequence_ratio": 0.90, "lcs_word_recall": 0.90},
        "failures": failures,
        "all_checks_passed": not failures,
        "records": records,
    }
    (WORK / "asr_qc.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"auditions": len(records), "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
