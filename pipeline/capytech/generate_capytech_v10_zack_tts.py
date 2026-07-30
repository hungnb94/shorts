#!/usr/bin/env python3
"""Generate provenance-locked Capytech V10 Zack narration.

This script intentionally has no duration-trimming path. It synthesizes once
per deterministic cache key, compresses and normalizes, fits only with the
pinned Rubber Band engine when necessary, then ASRs the fitted bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "spikes/001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))
from runtime_provenance import system_fingerprints, verified_model_snapshot, verify_environment  # noqa: E402

STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v10_zack_reaction_explainer_storyboard.json"
PROFILE = ROOT / "data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json"
WORK = ROOT / "output/projects/capytech/clips/capytech_v10_zack_reaction_explainer_work"
CACHE = WORK / "audio/cache"
OUTPUT = WORK / "audio/tts"
MANIFEST = WORK / "audio/tts_manifest.json"
ASR_PYTHON = Path("/usr/bin/python3")
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
PROFILE_ID = "ronald_wayne_zack_style_qwen"
REFERENCE_SHA256 = "73550032e52f99f02230d2bd0ca656b8627d936d086889a6534d51dc9541ca09"
MODEL_REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit"
MODEL_REVISION = "34ff5318365b59cba9c03ff729f2eee0814caf72"
WEIGHTS = {
    "model.safetensors": "b043693cb63f38f4e0ae5fe39a5cfdb466ef199dc5a767991a4a46235ac27e67",
    "speech_tokenizer/model.safetensors": "836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258",
}
RUBBERBAND_ENGINE_LABEL = "Rubber Band R3"
RUBBERBAND_CLI_VERSION = "4.0.0"
RUBBERBAND_PROVENANCE = f"{RUBBERBAND_ENGINE_LABEL} {RUBBERBAND_CLI_VERSION}"
MAX_TEMPO = 1.42
RATE = 48_000
V10_FFMPEG_FINGERPRINT = {
    "version_line": "ffmpeg version 7.1.1 Copyright (c) 2000-2025 the FFmpeg developers",
    "version_output_sha256": "88b12a030360dd4614c0e3999e442dd5cfa63c6df2b7b8dc2f23f56a40399ff9",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize(text: str) -> str:
    value = re.sub(r"['’]", "", text.lower())
    value = re.sub(r"\b1\s*,?\s*000\b", "one thousand", value)
    value = re.sub(r"\b300\b", "three hundred", value)
    value = re.sub(r"\b10\b", "ten", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=capture)


def duration(path: Path) -> float:
    result = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                  "-of", "default=nw=1:nk=1", str(path)], capture=True)
    return float(result.stdout.strip())


def ordered_tokens(expected: str, actual: str, max_insertions_ratio: float = 0.3) -> None:
    wanted, got = normalize(expected).split(), normalize(actual).split()
    cursor = 0
    matched_positions: list[int] = []
    for token in wanted:
        try:
            position = got.index(token, cursor)
        except ValueError as exc:
            raise RuntimeError(f"ordered ASR token missing after index {cursor}: {token}") from exc
        matched_positions.append(position)
        cursor = position + 1
    if len(got) - len(wanted) > max(2, int(len(wanted) * max_insertions_ratio)):
        raise RuntimeError(f"ASR has too many insertions: expected {len(wanted)}, got {len(got)}")
    for token in set(wanted):
        if got.count(token) > wanted.count(token) + 1:
            raise RuntimeError(f"ASR repeats expected token excessively: {token}")


def transcribe(path: Path) -> dict[str, Any]:
    code = (
        "import json,sys,mlx_whisper;"
        "r=mlx_whisper.transcribe(sys.argv[1],path_or_hf_repo=sys.argv[2],"
        "word_timestamps=True,language='en');print(json.dumps(r,ensure_ascii=False))"
    )
    payload = json.loads(run([str(ASR_PYTHON), "-c", code, str(path), ASR_MODEL], capture=True).stdout)
    words = [{"word": word["word"], "start": round(float(word["start"]), 4),
              "end": round(float(word["end"]), 4)}
             for segment in payload.get("segments", []) for word in segment.get("words", [])
             if word.get("word") and word.get("start") is not None and word.get("end") is not None]
    if not words:
        raise RuntimeError(f"No word timestamps for {path}")
    reconstructed = "".join(word["word"] for word in words).strip()
    return {"text": payload.get("text", reconstructed).strip(),
            "reconstructed_from_raw_tokens": reconstructed,
            "normalized": normalize(reconstructed), "words": words}


def assert_contract(
    profile: dict[str, Any], storyboard: dict[str, Any]
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    contract = storyboard["narrator_contract"]
    if profile["id"] != PROFILE_ID or contract["profile_id"] != PROFILE_ID:
        raise RuntimeError("Zack profile ID mismatch")
    if contract["profile_path"] != str(PROFILE.relative_to(ROOT)) \
            or sha256(PROFILE) != contract["profile_sha256"]:
        raise RuntimeError("Zack profile path/hash mismatch")
    reference = PROFILE.parent / profile["identity"]["reference_audio"]
    if sha256(reference) != REFERENCE_SHA256 \
            or profile["identity"]["reference_sha256"] != REFERENCE_SHA256 \
            or contract["reference_sha256"] != REFERENCE_SHA256:
        raise RuntimeError("Zack reference hash mismatch")
    model = profile["models"]["voice_clone"]
    if model["repo_id"] != MODEL_REPO or model["revision"] != MODEL_REVISION \
            or contract["model_repo"] != MODEL_REPO \
            or contract["model_revision"] != MODEL_REVISION:
        raise RuntimeError("Pinned model repo/revision mismatch")
    if {item["path"]: item["sha256"] for item in model["weights"]} != WEIGHTS \
            or contract["weight_sha256"] != WEIGHTS:
        raise RuntimeError("Pinned model weights mismatch")
    settings = profile["generation"]["clone"]
    expected_settings = contract["settings"]
    approved_settings = {
        "language": "English",
        "temperature": 0.7,
        "max_tokens": 768,
        "top_k": 30,
        "top_p": 0.9,
        "repetition_penalty": 1.5,
    }
    if expected_settings != approved_settings \
            or {key: settings.get(key) for key in approved_settings} != approved_settings:
        raise RuntimeError("Pinned generation settings mismatch")
    if profile["generation"]["seed"] != contract["seed"]:
        raise RuntimeError("Pinned seed mismatch")
    if contract["fitting"] != {
        "engine": "Rubber Band",
        "required_version": RUBBERBAND_PROVENANCE,
        "max_post_tempo": MAX_TEMPO,
        "hard_speech_trim_forbidden": True,
    }:
        raise RuntimeError("Storyboard fitting contract mismatch")
    if settings.get("max_post_tempo") != MAX_TEMPO \
            or settings.get("post_tempo_engine") != RUBBERBAND_PROVENANCE:
        raise RuntimeError("Pinned fitting contract mismatch")
    version_result = run(["rubberband", "--version"], capture=True)
    version = "\n".join(part.strip() for part in (version_result.stdout, version_result.stderr)
                        if part.strip())
    match = re.search(r"(?<!\d)(\d+\.\d+\.\d+)(?!\d)", version)
    if not match or match.group(1) != RUBBERBAND_CLI_VERSION:
        raise RuntimeError(f"Rubber Band version mismatch: {version!r}")
    environment_record = verify_environment(profile, SPIKE, "synthesis")
    actual_system = system_fingerprints()
    profile_expected = profile["runtime"]["repeatability_fingerprints"]
    if actual_system["platform"] != profile_expected["platform"]:
        raise RuntimeError(
            f"Platform fingerprint mismatch: expected {profile_expected['platform']}, "
            f"got {actual_system['platform']}"
        )
    if actual_system["ffmpeg"] != V10_FFMPEG_FINGERPRINT:
        raise RuntimeError(
            f"V10 FFmpeg fingerprint mismatch: expected {V10_FFMPEG_FINGERPRINT}, "
            f"got {actual_system['ffmpeg']}"
        )
    runtime_record = {
        "policy": "V10_REVIEWED_FFMPEG_RUNTIME_OVERRIDE_PROFILE_UNCHANGED",
        "reason": "The approved voice/model/reference pins are unchanged; local FFmpeg differs from the profile's historical repeatability fingerprint.",
        "profile_expected": profile_expected,
        "actual": actual_system,
        "synthesis_environment": environment_record,
    }
    snapshot, snapshot_record = verified_model_snapshot(model)
    for relative, expected in WEIGHTS.items():
        if sha256(snapshot / relative) != expected:
            raise RuntimeError(f"Snapshot weight hash mismatch: {relative}")
    return snapshot, snapshot_record, runtime_record


def fit_and_pad(source: Path, output: Path, speech_seconds: float, tempo: float) -> str:
    fitted = output.with_suffix(".fitted.wav")
    if tempo > 1.0 + 1e-6:
        result = run(["rubberband", "--fine", "--tempo", f"{tempo:.8f}",
                      str(source), str(fitted)], capture=True)
        engine_log = "\n".join((result.stdout, result.stderr))
        if "Using R3 (finer) engine" not in engine_log or "Using R2" in engine_log:
            raise RuntimeError("Rubber Band did not confirm the pinned R3 fine engine")
        observed_engine = "R3_FINE"
    else:
        shutil.copyfile(source, fitted)
        observed_engine = "BYPASS_TEMPO_1_0"
    # Padding is real PCM. No atrim, -t, sample slicing, or timestamp-only delay is used.
    pre, post = 0.10, 0.22
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
         "-t", f"{pre:.3f}", "-i", f"anullsrc=r={RATE}:cl=stereo", "-i", str(fitted),
         "-f", "lavfi", "-t", f"{post:.3f}", "-i", f"anullsrc=r={RATE}:cl=stereo",
         "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]",
         "-map", "[a]", "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(output)])
    fitted.unlink()
    return observed_engine


def main() -> None:
    for path in (STORYBOARD, PROFILE, ASR_PYTHON):
        if not path.is_file():
            raise FileNotFoundError(path)
    for executable in ("ffmpeg", "ffprobe", "rubberband"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable unavailable: {executable}")
    storyboard = json.loads(STORYBOARD.read_text())
    profile = json.loads(PROFILE.read_text())
    snapshot, snapshot_record, runtime_record = assert_contract(profile, storyboard)
    settings = profile["generation"]["clone"]
    generation_settings = {key: settings[key] for key in
                           ("language", "temperature", "max_tokens", "top_k", "top_p", "repetition_penalty")}
    fitting_settings = {"engine": "Rubber Band", "engine_label": RUBBERBAND_ENGINE_LABEL,
                        "cli_version": RUBBERBAND_CLI_VERSION,
                        "version": RUBBERBAND_PROVENANCE,
                        "max_post_tempo": MAX_TEMPO, "mode": "R3_FINE", "command_flag": "--fine",
                        "pre_roll_seconds": 0.10, "post_roll_min_seconds": 0.20}
    model = load_model(str(snapshot))
    CACHE.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    previous_end = -1.0
    for index, line in enumerate(storyboard["tts_contract"]["lines"]):
        envelope_start, envelope_end = map(float, line["envelope"])
        guard_start, guard_end = map(float, line["speech_guard"])
        if envelope_start < previous_end - 1e-9:
            raise RuntimeError(f"Narration envelopes overlap at {line['id']}")
        previous_end = envelope_end
        available_speech = guard_end - guard_start
        seed = int(profile["generation"]["seed"]) + index
        key_payload = {"line_id": line["id"], "normalized_text": normalize(line["text"]), "seed": seed,
                       "profile_sha256": sha256(PROFILE), "reference_sha256": REFERENCE_SHA256,
                       "model_repo": MODEL_REPO, "model_revision": MODEL_REVISION, "weights": WEIGHTS,
                       "generation": generation_settings, "fitting": fitting_settings}
        cache_key = hashlib.sha256(canonical(key_payload).encode()).hexdigest()
        normalized = CACHE / f"{cache_key}.normalized.wav"
        if not normalized.exists():
            mx.random.seed(seed)
            generated = list(model.generate(text=line["text"], ref_audio=str(PROFILE.parent / profile["identity"]["reference_audio"]),
                                             ref_text=profile["identity"]["reference_text"],
                                             lang_code=settings["language"], temperature=settings["temperature"],
                                             max_tokens=settings["max_tokens"], top_k=settings["top_k"],
                                             top_p=settings["top_p"], repetition_penalty=settings["repetition_penalty"],
                                             stream=False))
            if not generated:
                raise RuntimeError(f"No synthesized audio for {line['id']}")
            raw = CACHE / f"{cache_key}.raw.wav"
            audio = np.concatenate([np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in generated])
            sf.write(raw, audio, int(generated[0].sample_rate), subtype="PCM_16")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
                 "-af", "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
                        "loudnorm=I=-16:TP=-1.5:LRA=10",
                 "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(normalized)])
            raw.unlink()
        measured = duration(normalized)
        required_tempo = max(1.0, measured / available_speech)
        if required_tempo > MAX_TEMPO + 1e-9:
            raise RuntimeError(f"{line['id']} requires {required_tempo:.4f}x > {MAX_TEMPO}; rewrite line")
        output = OUTPUT / f"{index:02d}_{line['id']}.wav"
        observed_engine = fit_and_pad(normalized, output, available_speech, required_tempo)
        asr = transcribe(output)
        ordered_tokens(line["expected_normalized_asr"], asr["normalized"])
        first_word, last_word = asr["words"][0], asr["words"][-1]
        absolute_onset = envelope_start + float(first_word["start"])
        absolute_end = envelope_start + float(last_word["end"])
        if absolute_onset < guard_start - 0.03 or absolute_end > guard_end + 0.03:
            raise RuntimeError(f"{line['id']} intelligible speech violates guard: {absolute_onset:.3f}-{absolute_end:.3f}")
        if line["id"] == "hook" and absolute_end + 0.12 > 5.0:
            raise RuntimeError("Hook plus 120ms transition cannot fit before baseline narration")
        records.append({"id": line["id"], "source_text": line["text"],
                        "expected_normalized_asr": line["expected_normalized_asr"],
                        "envelope": line["envelope"], "speech_guard": line["speech_guard"],
                        "seed": seed, "cache_key": cache_key, "cache_inputs": key_payload,
                        "path": str(output.relative_to(ROOT)), "sha256": sha256(output),
                        "unfitted_duration_seconds": round(measured, 4),
                        "fitted_duration_seconds": round(duration(output), 4),
                        "measured_tempo": round(required_tempo, 8),
                        "tempo_engine_observed": observed_engine,
                        "speech_onset_seconds_absolute": round(absolute_onset, 4),
                        "speech_end_seconds_absolute": round(absolute_end, 4), "asr": asr})
    manifest = {"schema_version": 2, "status": "CANONICAL_TTS_GENERATED",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "storyboard_path": str(STORYBOARD.relative_to(ROOT)), "storyboard_sha256": sha256(STORYBOARD),
                "generator_path": str(Path(__file__).resolve().relative_to(ROOT)),
                "generator_sha256": sha256(Path(__file__).resolve()),
                "profile": {"path": str(PROFILE.relative_to(ROOT)), "id": PROFILE_ID,
                            "sha256": sha256(PROFILE), "reference_sha256": REFERENCE_SHA256},
                "model": {"repo": MODEL_REPO, "revision": MODEL_REVISION, "weights": WEIGHTS,
                          "snapshot_record": snapshot_record},
                "runtime": runtime_record,
                "generation_settings": generation_settings, "fitting_settings": fitting_settings,
                "asr_engine": {"python": str(ASR_PYTHON), "model": ASR_MODEL, "word_timestamps": True},
                "lines": records}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS: {len(records)} Zack lines -> {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
