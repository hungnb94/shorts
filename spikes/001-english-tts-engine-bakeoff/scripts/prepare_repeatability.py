#!/usr/bin/env python3
import json
import re
import subprocess
import wave
from pathlib import Path
from typing import Any

from runtime_provenance import locked_packages, sha256, system_fingerprints

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
WORK = SPIKE / "work"
RUN_IDS = ("run_a", "run_b")
ORDER = tuple(item["id"] for item in CORPUS)
BOUNDS = {item["id"]: item["duration_bounds_seconds"] for item in CORPUS}
SILENCE_SECONDS = 0.75
NORMALIZATION = "ffmpeg loudnorm I=-16 TP=-1.5 LRA=11; mono 48kHz PCM s16le"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


def probe(path: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ]
    )
    return json.loads(result.stdout)


def volume(path: Path) -> dict[str, float | None]:
    result = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(path),
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ]
    )
    mean = re.search(r"mean_volume:\s*(-?[0-9.]+) dB", result.stderr)
    peak = re.search(r"max_volume:\s*(-?[0-9.]+) dB", result.stderr)
    return {
        "mean_db": float(mean.group(1)) if mean else None,
        "peak_db": float(peak.group(1)) if peak else None,
    }


def clear_wavs(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for path in directory.rglob("*.wav"):
        path.unlink()


def concatenate(paths: list[Path], output: Path) -> float:
    silence = b"\x00\x00" * int(48000 * SILENCE_SECONDS)
    total_frames = 0
    with wave.open(str(output), "wb") as destination:
        destination.setnchannels(1)
        destination.setsampwidth(2)
        destination.setframerate(48000)
        for index, path in enumerate(paths):
            with wave.open(str(path), "rb") as source:
                if (source.getnchannels(), source.getsampwidth(), source.getframerate()) != (
                    1,
                    2,
                    48000,
                ):
                    raise RuntimeError(f"Unexpected WAV format: {path}")
                frames = source.readframes(source.getnframes())
                destination.writeframes(frames)
                total_frames += source.getnframes()
            if index != len(paths) - 1:
                destination.writeframes(silence)
                total_frames += int(48000 * SILENCE_SECONDS)
    return total_frames / 48000


def expected_environment() -> dict[str, Any]:
    specification = PROFILE["runtime"]["environments"]["synthesis"]
    return {
        "name": "synthesis",
        "python": specification["python"],
        "python_implementation": "cpython",
        "lock_file": specification["lock_file"],
        "lock_sha256": specification["lock_sha256"],
        "packages": dict(
            sorted(locked_packages(SPIKE / specification["lock_file"]).items())
        ),
    }


def expected_model_resolution() -> dict[str, Any]:
    model = PROFILE["models"]["voice_clone"]
    return {
        "repo_id": model["repo_id"],
        "requested_revision": model["revision"],
        "resolved_revision": model["revision"],
        "weights": model["weights"],
    }


def validate_generation(
    run_id: str, generation: dict[str, Any], failures: list[str]
) -> dict[str, dict[str, Any]]:
    prefix = f"generation {run_id}"
    exact_fields = {
        "run_id": run_id,
        "profile_id": PROFILE["id"],
        "strategy": PROFILE["runtime"]["strategy"],
        "model": PROFILE["models"]["voice_clone"],
        "settings": PROFILE["generation"]["clone"],
        "reference_sha256": PROFILE["identity"]["reference_sha256"],
        "seed_policy": (
            f"{PROFILE['generation']['seed']} + stable corpus index; reset before each item"
        ),
        "runtime_environment": expected_environment(),
        "system_fingerprints": PROFILE["runtime"]["repeatability_fingerprints"],
    }
    for field, expected in exact_fields.items():
        if generation.get(field) != expected:
            failures.append(f"{prefix}: {field} mismatch")

    resolution = generation.get("model_resolution")
    expected_resolution = expected_model_resolution()
    if not isinstance(resolution, dict):
        failures.append(f"{prefix}: missing model_resolution")
    else:
        for field, expected in expected_resolution.items():
            if resolution.get(field) != expected:
                failures.append(f"{prefix}: model_resolution.{field} mismatch")
        snapshot = resolution.get("local_snapshot")
        if not isinstance(snapshot, str) or not Path(snapshot).is_absolute():
            failures.append(f"{prefix}: model_resolution.local_snapshot is not absolute")

    records = generation.get("records")
    if not isinstance(records, list) or len(records) != len(CORPUS):
        failures.append(f"{prefix}: corpus record count/order mismatch")
        return {}

    by_sample: dict[str, dict[str, Any]] = {}
    work_root = WORK.resolve()
    for index, sample in enumerate(CORPUS):
        record = records[index]
        if not isinstance(record, dict):
            failures.append(f"{prefix}: record {index} is not an object")
            continue
        sample_id = sample["id"]
        expected_output = f"raw/{run_id}/{sample_id}.wav"
        expected_record_fields = {
            "sample_id": sample_id,
            "run_id": run_id,
            "source_text": sample["text"],
            "output": expected_output,
        }
        for field, expected in expected_record_fields.items():
            if record.get(field) != expected:
                failures.append(f"{prefix}/{sample_id}: {field} mismatch")
        output_value = record.get("output")
        if not isinstance(output_value, str):
            continue
        source = WORK / output_value
        try:
            contained = source.resolve().is_relative_to(work_root)
        except (OSError, RuntimeError):
            contained = False
        if not contained:
            failures.append(f"{prefix}/{sample_id}: output escapes work directory")
            continue
        if not source.is_file():
            failures.append(f"{prefix}/{sample_id}: output file missing")
            continue
        actual_hash = sha256(source)
        if record.get("sha256") != actual_hash:
            failures.append(f"{prefix}/{sample_id}: recorded file hash mismatch")
        by_sample[sample_id] = record
    if tuple(by_sample) != ORDER:
        failures.append(f"{prefix}: corpus text/order mismatch")
    return by_sample


def write_manifest(manifest: dict[str, Any]) -> None:
    (WORK / "repeatability_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    fingerprints = system_fingerprints()
    if fingerprints != PROFILE["runtime"]["repeatability_fingerprints"]:
        failures.append("current FFmpeg/platform fingerprint mismatch")
    generations: dict[str, dict[str, Any]] = {}
    validated: dict[str, dict[str, dict[str, Any]]] = {}
    for run_id in RUN_IDS:
        path = WORK / f"generation_{run_id}.json"
        if not path.is_file():
            failures.append(f"generation {run_id}: manifest missing")
            continue
        try:
            generation = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as error:
            failures.append(f"generation {run_id}: invalid manifest: {error}")
            continue
        if not isinstance(generation, dict):
            failures.append(f"generation {run_id}: manifest is not an object")
            continue
        generations[run_id] = generation
        validated[run_id] = validate_generation(run_id, generation, failures)

    base_manifest: dict[str, Any] = {
        "profile_id": PROFILE["id"],
        "normalization": NORMALIZATION,
        "synthesis_environment": expected_environment(),
        "system_fingerprints": fingerprints,
        "all_checks_passed": False,
        "failures": failures,
        "records": [],
        "auditions": [],
        "cross_process_comparisons": [],
    }
    if failures:
        write_manifest(base_manifest)
        print(json.dumps({"failures": failures}, indent=2))
        raise SystemExit(1)

    normalized_root = WORK / "normalized"
    audition_root = WORK / "audition"
    clear_wavs(normalized_root)
    clear_wavs(audition_root)
    records = []
    for run_id in RUN_IDS:
        output_dir = normalized_root / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        for sample_id in ORDER:
            record = validated[run_id][sample_id]
            source = WORK / record["output"]
            output = output_dir / f"{sample_id}.wav"
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(source),
                    "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar",
                    "48000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(output),
                ]
            )
            run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"])
            metadata = probe(output)
            stream = metadata["streams"][0]
            duration = float(metadata["format"]["duration"])
            levels = volume(output)
            low, high = BOUNDS[sample_id]
            checks = {
                "duration_in_bounds": low <= duration <= high,
                "sample_rate_48000": stream.get("sample_rate") == "48000",
                "mono": stream.get("channels") == 1,
                "pcm_s16le": stream.get("codec_name") == "pcm_s16le",
                "not_silent": levels["mean_db"] is not None and levels["mean_db"] > -50.0,
                "decoded_fully": True,
            }
            if not all(checks.values()):
                failures.append(f"{run_id}/{sample_id}: output checks failed: {checks}")
            records.append(
                {
                    **record,
                    "raw_sha256": sha256(source),
                    "normalized_file": str(output.relative_to(WORK)),
                    "normalized_sha256": sha256(output),
                    "duration_seconds": round(duration, 3),
                    "mean_db": levels["mean_db"],
                    "peak_db": levels["peak_db"],
                    "checks": checks,
                }
            )

    auditions = []
    for run_id in RUN_IDS:
        paths = [normalized_root / run_id / f"{sample_id}.wav" for sample_id in ORDER]
        output = audition_root / f"{run_id}.wav"
        duration = concatenate(paths, output)
        run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"])
        auditions.append(
            {
                "run_id": run_id,
                "file": str(output.relative_to(WORK)),
                "duration_seconds": round(duration, 3),
                "sha256": sha256(output),
                "sample_order": list(ORDER),
            }
        )

    by_key = {(record["run_id"], record["sample_id"]): record for record in records}
    comparisons = []
    for sample_id in ORDER:
        a = by_key[("run_a", sample_id)]
        b = by_key[("run_b", sample_id)]
        comparison = {
            "sample_id": sample_id,
            "raw_hash_equal": a["raw_sha256"] == b["raw_sha256"],
            "normalized_hash_equal": a["normalized_sha256"] == b["normalized_sha256"],
            "duration_delta_seconds": round(
                abs(a["duration_seconds"] - b["duration_seconds"]), 6
            ),
        }
        if not comparison["raw_hash_equal"]:
            failures.append(f"{sample_id}: raw hash mismatch between run_a and run_b")
        if not comparison["normalized_hash_equal"]:
            failures.append(
                f"{sample_id}: normalized hash mismatch between run_a and run_b"
            )
        comparisons.append(comparison)

    manifest = {
        **base_manifest,
        "all_checks_passed": not failures,
        "failures": failures,
        "records": records,
        "auditions": auditions,
        "cross_process_comparisons": comparisons,
    }
    write_manifest(manifest)
    print(
        json.dumps(
            {
                "normalized_files": len(records),
                "audition_files": len(auditions),
                "failures": failures,
                "comparisons": comparisons,
            },
            indent=2,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
