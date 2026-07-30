#!/usr/bin/env python3
"""Fail-closed exact-final verifier for Capytech V9 Real Drop."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "output/projects/capytech/final/2026-07-30-capytech_v9_real_drop.mp4"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v9_real_drop_storyboard.json"
TTS_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work/audio/tts_manifest.json"
RENDER_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work/render_manifest.json"
FINAL_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/final_render_manifest.json"
SOURCE_USAGE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/source_usage.json"
SOURCE_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json"
HOOK_GATE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/hook_gate.json"
RESULT_GATE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/result_blind_test.json"
REACTION_GATE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/reaction_blind_test.json"
QC = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc"
REPORT = QC / "final_qc.json"
ASR_PYTHON = Path("/usr/bin/python3")
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
EXPECTED_DURATION = 58.0
FPS = 30


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=ROOT, check=check, text=True, capture_output=True
    )


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def normalize(text: str) -> str:
    value = re.sub(r"['’]", "", text.lower())
    value = re.sub(r"\b1\s*,?\s*000\b", "one thousand", value)
    value = re.sub(r"\b300\b", "three hundred", value)
    value = re.sub(r"\b10\b", "ten", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def rate_is_30(value: str | None) -> bool:
    if not value or "/" not in value:
        return False
    numerator, denominator = map(int, value.split("/", 1))
    return denominator != 0 and abs(numerator / denominator - FPS) < 1e-9


def parse_loudnorm(stderr: str) -> dict[str, Any]:
    start, end = stderr.rfind("{"), stderr.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("loudnorm JSON missing")
    return json.loads(stderr[start:end + 1])


def extract_frame(timestamp: float, output: Path, width: int = 270, height: int = 480) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    result = run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{timestamp:.3f}", "-i", str(FINAL), "-frames:v", "1",
            "-vf", f"scale={width}:{height}:flags=lanczos", str(output),
        ],
        check=False,
    )
    if result.returncode or not output.is_file() or output.stat().st_size < 4_000:
        raise RuntimeError(f"Frame extraction failed at {timestamp:.3f}s")


def make_sheet(
    items: list[tuple[str, float, Path]],
    output: Path,
    columns: int = 6,
) -> None:
    tile_w, tile_h = 234, 432
    canvas = Image.new(
        "RGB", (columns * tile_w, math.ceil(len(items) / columns) * tile_h), "#e5e7eb"
    )
    draw = ImageDraw.Draw(canvas)
    for index, (label, timestamp, path) in enumerate(items):
        image = Image.open(path).convert("RGB")
        image.thumbnail((216, 384))
        x, y = (index % columns) * tile_w, (index // columns) * tile_h
        canvas.paste(image, (x + 9, y + 42))
        draw.text((x + 6, y + 5), f"{label} {timestamp:.2f}s", fill="#111827")
    canvas.save(output, quality=94)


def dense_sheet(name: str, start: float, end: float, step: float = 0.25) -> tuple[Path, list[Path]]:
    directory = QC / "exact_final_evidence" / name
    items: list[tuple[str, float, Path]] = []
    timestamp = start
    # Timeline windows are half-open: a 58.0-second asset has no frame at t=58.0.
    while timestamp < end - 1e-7:
        output = directory / f"{timestamp:05.2f}.jpg"
        extract_frame(timestamp, output)
        items.append((name, timestamp, output))
        timestamp = round(timestamp + step, 6)
    sheet_path = QC / f"{name}_sheet.jpg"
    make_sheet(items, sheet_path)
    return sheet_path, [item[2] for item in items]


def asr_window(name: str, start: float, end: float) -> dict[str, Any]:
    directory = QC / "asr"
    directory.mkdir(parents=True, exist_ok=True)
    wav = directory / f"{name}.wav"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(start), "-t", str(end - start), "-i", str(FINAL),
            "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav),
        ]
    )
    code = (
        "import json,sys,mlx_whisper;"
        "r=mlx_whisper.transcribe(sys.argv[1],path_or_hf_repo=sys.argv[2],"
        "word_timestamps=True,language='en');"
        "print(json.dumps(r,ensure_ascii=False))"
    )
    result = run([str(ASR_PYTHON), "-c", code, str(wav), ASR_MODEL])
    payload = json.loads(result.stdout)
    words = [
        word
        for segment in payload.get("segments", [])
        for word in segment.get("words", [])
    ]
    reconstructed = "".join(str(word.get("word", "")) for word in words).strip()
    record = {
        "window": [start, end],
        "wav": rel(wav),
        "wav_sha256": sha256(wav),
        "text": payload.get("text", reconstructed).strip(),
        "reconstructed_from_raw_tokens": reconstructed,
        "normalized": normalize(reconstructed),
        "words": words,
    }
    (directory / f"{name}.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    )
    return record


def contains_expected(actual: str, expected: str) -> bool:
    actual_words = set(normalize(actual).split())
    required = set(normalize(expected).split()) - {"a", "an", "the", "this", "it", "to"}
    return required <= actual_words


def bottom_luma_scan() -> dict[str, Any]:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for whole-timeline luma verification") from exc
    capture = cv2.VideoCapture(str(FINAL))
    samples: list[dict[str, float]] = []
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % 15 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            samples.append(
                {
                    "time": round(index / FPS, 3),
                    "bottom_16": float(gray[-16:, :].mean()),
                    "bottom_96": float(gray[-96:, :].mean()),
                }
            )
        index += 1
    capture.release()
    if not samples:
        raise RuntimeError("No frames read for bottom-luma scan")
    return {
        "sample_interval_seconds": 0.5,
        "sample_count": len(samples),
        "bottom_16_min": min(item["bottom_16"] for item in samples),
        "bottom_96_min": min(item["bottom_96"] for item in samples),
        "samples": samples,
    }


def rms_slice(start: float, duration: float = 0.1) -> float:
    result = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}",
            "-t", f"{duration:.3f}", "-i", str(FINAL),
            "-af", "volumedetect", "-f", "null", "-",
        ],
        check=False,
    )
    match = re.search(r"mean_volume:\s*(-?(?:inf|\d+(?:\.\d+)?)) dB", result.stderr)
    if not match:
        raise RuntimeError(f"Unable to measure audio slice at {start:.3f}s")
    return -120.0 if match.group(1) == "-inf" else float(match.group(1))


def audio_boundary_scan() -> list[dict[str, Any]]:
    boundaries = [0.8, 1.6, 2.4, 3, 8, 11, 18, 22, 29, 34, 36, 37.5, 39, 45.5, 49, 55.5, 56]
    return [
        {
            "boundary": boundary,
            "before_db": rms_slice(max(0, boundary - 0.1)),
            "after_db": rms_slice(boundary),
        }
        for boundary in boundaries
    ]


def main() -> int:
    for path in (
        FINAL, STORYBOARD, TTS_MANIFEST, RENDER_MANIFEST, FINAL_MANIFEST,
        SOURCE_USAGE, SOURCE_MANIFEST, HOOK_GATE, RESULT_GATE, REACTION_GATE,
        ASR_PYTHON,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    QC.mkdir(parents=True, exist_ok=True)
    storyboard = load(STORYBOARD)
    tts = load(TTS_MANIFEST)
    render_manifest = load(RENDER_MANIFEST)
    final_manifest = load(FINAL_MANIFEST)
    source_usage = load(SOURCE_USAGE)
    source_manifest = load(SOURCE_MANIFEST)
    final_hash = sha256(FINAL)

    info = json.loads(
        run(
            [
                "ffprobe", "-v", "error", "-count_frames", "-show_streams",
                "-show_format", "-of", "json", str(FINAL),
            ]
        ).stdout
    )
    videos = [stream for stream in info["streams"] if stream.get("codec_type") == "video"]
    audios = [stream for stream in info["streams"] if stream.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise RuntimeError("Exact final must contain one video and one audio stream")
    video, audio = videos[0], audios[0]
    duration = float(info["format"]["duration"])
    decoded_frames = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
    gates: dict[str, bool] = {
        "duration_58_seconds": abs(duration - EXPECTED_DURATION) <= 0.10,
        "duration_in_project_range": 50 <= duration <= 75,
        "native_1080x1920": video.get("width") == 1080 and video.get("height") == 1920,
        "h264_yuv420p": video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p",
        "cfr_30fps": rate_is_30(video.get("r_frame_rate")) and rate_is_30(video.get("avg_frame_rate")),
        "exact_frame_count": decoded_frames == round(EXPECTED_DURATION * FPS),
        "aac_48k_stereo": (
            audio.get("codec_name") == "aac"
            and audio.get("sample_rate") == "48000"
            and audio.get("channels") == 2
        ),
    }

    decode = run(
        ["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"],
        check=False,
    )
    gates["full_decode"] = decode.returncode == 0 and not decode.stderr.strip()
    detector = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
            "-vf", "blackdetect=d=0.20:pix_th=0.10,freezedetect=n=-60dB:d=1.0",
            "-af", "silencedetect=n=-48dB:d=0.75", "-f", "null", "-",
        ],
        check=False,
    )
    (QC / "detectors.log").write_text(detector.stderr)
    black = re.findall(r"black_start:[^\n]+", detector.stderr)
    freeze = re.findall(r"freeze_start:[^\n]+", detector.stderr)
    silence = re.findall(r"silence_start:[^\n]+", detector.stderr)
    gates["detectors_executed"] = detector.returncode == 0
    gates["no_black_events"] = detector.returncode == 0 and not black
    gates["no_freeze_events"] = detector.returncode == 0 and not freeze
    gates["no_silence_events"] = detector.returncode == 0 and not silence

    loud = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json",
            "-f", "null", "-",
        ],
        check=False,
    )
    loudness = parse_loudnorm(loud.stderr) if loud.returncode == 0 else {}
    (QC / "loudness.json").write_text(json.dumps(loudness, indent=2) + "\n")
    integrated = float(loudness.get("input_i", 999))
    true_peak = float(loudness.get("input_tp", 999))
    gates["loudness_measurement"] = loud.returncode == 0
    gates["integrated_loudness"] = -17.0 <= integrated <= -15.0
    gates["true_peak"] = true_peak <= -1.5

    luma = bottom_luma_scan()
    (QC / "bottom_luma.json").write_text(json.dumps(luma, indent=2) + "\n")
    gates["no_persistent_black_bottom_band"] = (
        luma["bottom_16_min"] >= 5.0 and luma["bottom_96_min"] >= 7.0
    )
    boundary_audio = audio_boundary_scan()
    (QC / "audio_boundary_slices.json").write_text(
        json.dumps(boundary_audio, indent=2) + "\n"
    )
    gates["audio_boundary_scan_complete"] = len(boundary_audio) == 17
    gates["no_boundary_slice_is_silent"] = all(
        item["before_db"] > -60 and item["after_db"] > -60 for item in boundary_audio
    )

    asr = {
        "hook": asr_window("hook", 0.0, 3.0),
        "body": asr_window("body", 3.0, 38.0),
        "cta": asr_window("cta", 38.0, 42.0),
        "payoff": asr_window("payoff", 42.0, 58.0),
    }
    expected = {line["id"]: line["expected_normalized_asr"] for line in storyboard["tts_contract"]["lines"]}
    gates["hook_asr_audited"] = "normalized" in asr["hook"]
    gates["body_asr"] = all(
        contains_expected(asr["body"]["normalized"], expected[line_id])
        for line_id in ("waist", "ten", "three_hundred", "thousand_setup")
    )
    gates["cta_spoken_exact_contract"] = contains_expected(
        asr["cta"]["normalized"], storyboard["cta"]["expected_normalized_asr"]
    )
    gates["cta_spoken_like_subscribe_comment"] = all(
        word in asr["cta"]["normalized"] for word in ("like", "subscribe", "comment")
    )
    gates["payoff_asr"] = all(
        contains_expected(asr["payoff"]["normalized"], expected[line_id])
        for line_id in ("surface_context", "payoff", "loop")
    )

    sheet_specs = {
        "hook_0_3": (0.0, 3.0, 0.2),
        "waist_action_result": (3.0, 11.0, 0.5),
        "ten_stories_action_result": (11.0, 22.0, 0.5),
        "three_hundred_action_result": (22.0, 34.0, 0.5),
        "thousand_setup_illustration_drop": (34.0, 49.0, 0.5),
        "cta_38_42": (38.0, 42.0, 0.2),
        "powered_payoff": (49.0, 56.0, 0.25),
        "loop_56_58": (56.0, 58.0, 0.2),
        "caption_onset": (0.0, 0.4, 0.1),
    }
    sheets: list[Path] = []
    frames: list[Path] = []
    for name, (start, end, step) in sheet_specs.items():
        sheet_path, frame_paths = dense_sheet(name, start, end, step)
        sheets.append(sheet_path)
        frames.extend(frame_paths)
    evidence_hashes = {
        rel(path): sha256(path)
        for path in sheets + frames
    }

    assessment_path = QC / "exact_final_visual_assessment.json"
    assessment = load(assessment_path) if assessment_path.exists() else {}
    if (
        assessment.get("artifact_sha256") != final_hash
        or assessment.get("evidence_sha256") != evidence_hashes
    ):
        assessment = {
            "artifact_sha256": final_hash,
            "evidence_sha256": evidence_hashes,
            "reviewer": "",
            "reviewed_at_utc": "",
            "status": "UNVERIFIED",
            "checks": {
                "caption_visible_by_0_2": False,
                "komika_calibrated_geometry": False,
                "caption_bursts_2_to_5_words": False,
                "one_animated_emphasized_keyword_per_burst": False,
                "caption_center_55_to_65_percent": False,
                "early_sfx_matches_hook_event": False,
                "event_sfx_matches_impacts_and_reveals": False,
                "cta_visuals_like_subscribe_comment_38_to_42": False,
                "cta_action_continues_underneath": False,
                "capytech_brand_visible_during_cta": False,
                "moving_watermark_changes_position": False,
                "citations_visible_and_readable": False,
                "illustration_label_visible_for_entire_pexels_window": False,
                "different_devices_surfaces_methods_disclaimer_readable": False,
                "categorical_outcomes_truthful": False,
                "round4_real_drop_tracking_ring_zoom_annotation": False,
                "round4_avoids_long_red_dirt_monotony": False,
                "powered_display_result_unambiguous": False,
                "reaction_silhouettes_distinguishable": False,
                "information_progression_and_visual_cadence": False,
                "loop_payoff_closure": False,
            },
            "notes": {},
        }
        assessment_path.write_text(json.dumps(assessment, indent=2) + "\n")
    checks = assessment.get("checks", {})
    required_visual_checks = {
        "caption_visible_by_0_2",
        "komika_calibrated_geometry",
        "caption_bursts_2_to_5_words",
        "one_animated_emphasized_keyword_per_burst",
        "caption_center_55_to_65_percent",
        "early_sfx_matches_hook_event",
        "event_sfx_matches_impacts_and_reveals",
        "cta_visuals_like_subscribe_comment_38_to_42",
        "cta_action_continues_underneath",
        "capytech_brand_visible_during_cta",
        "moving_watermark_changes_position",
        "citations_visible_and_readable",
        "illustration_label_visible_for_entire_pexels_window",
        "different_devices_surfaces_methods_disclaimer_readable",
        "categorical_outcomes_truthful",
        "round4_real_drop_tracking_ring_zoom_annotation",
        "round4_avoids_long_red_dirt_monotony",
        "powered_display_result_unambiguous",
        "reaction_silhouettes_distinguishable",
        "information_progression_and_visual_cadence",
        "loop_payoff_closure",
    }
    gates["exact_final_visual_review_hash_bound"] = (
        assessment.get("artifact_sha256") == final_hash
        and assessment.get("evidence_sha256") == evidence_hashes
    )
    gates["exact_final_visual_review_verified"] = (
        assessment.get("status") in {"VERIFIED", "VERIFIED_MACHINE_PROXY"}
        and bool(assessment.get("reviewer"))
        and assessment.get("reviewer_type") in {"human", "machine_proxy"}
        and bool(assessment.get("reviewed_at_utc"))
        and set(checks) == required_visual_checks
        and all(checks.values())
    )

    occurrences = source_usage.get("occurrences", [])
    youtube_occurrences = [item for item in occurrences if item.get("kind") == "youtube"]
    source_durations = {
        source["youtube_id"]: float(source["source_duration_seconds"])
        for source in source_manifest["sources"]
    }
    aggregates = source_usage.get("aggregate_youtube_usage_seconds", {})
    gates["source_usage_hash_bound"] = (
        render_manifest.get("source_usage_sha256") == sha256(SOURCE_USAGE)
        and final_manifest.get("source_usage_sha256") == sha256(SOURCE_USAGE)
    )
    gates["all_retained_windows_under_15_seconds"] = bool(youtube_occurrences) and all(
        float(item["final_end"]) - float(item["final_start"]) < 15
        for item in youtube_occurrences
    )
    gates["each_source_below_50_percent"] = all(
        float(seconds) < source_durations[video_id] * 0.5
        for video_id, seconds in aggregates.items()
    )
    gates["commentary_present"] = bool(tts.get("lines")) and gates["body_asr"] and gates["payoff_asr"]
    gates["at_least_two_post_render_value_adds"] = len(final_manifest.get("value_adds", [])) >= 2
    gates["final_manifest_exact_artifact"] = final_manifest.get("artifact_sha256") == final_hash
    gates["renderer_provenance"] = (
        final_manifest.get("renderer_sha256") == render_manifest.get("renderer_sha256")
    )
    gates["storyboard_provenance"] = (
        render_manifest.get("storyboard_sha256") == sha256(STORYBOARD)
        and final_manifest.get("storyboard_sha256") == sha256(STORYBOARD)
    )
    gates["tts_provenance"] = (
        render_manifest.get("tts_manifest_sha256") == sha256(TTS_MANIFEST)
        and final_manifest.get("tts_manifest_sha256") == sha256(TTS_MANIFEST)
    )

    hook_gate = load(HOOK_GATE)
    result_gate = load(RESULT_GATE)
    reaction_gate = load(REACTION_GATE)
    gates["preflight_hook_hash_bound"] = (
        storyboard["bindings"]["hook_gate"]["sha256"] == sha256(HOOK_GATE)
    )
    gates["preflight_result_hash_bound"] = (
        storyboard["bindings"]["result_blind_test"]["sha256"] == sha256(RESULT_GATE)
    )
    gates["preflight_reaction_hash_bound"] = (
        storyboard["bindings"]["reaction_blind_test"]["sha256"] == sha256(REACTION_GATE)
    )

    evidence_manifest = {
        "schema_version": 1,
        "artifact": rel(FINAL),
        "artifact_sha256": final_hash,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sheets": [rel(path) for path in sheets],
        "evidence_sha256": evidence_hashes,
        "visual_assessment": rel(assessment_path),
        "visual_assessment_sha256": sha256(assessment_path),
        "preflight": {
            "hook": {"sha256": sha256(HOOK_GATE), "decision": hook_gate.get("decision")},
            "results": {"sha256": sha256(RESULT_GATE), "decision": result_gate.get("gate_decision")},
            "reactions": {"sha256": sha256(REACTION_GATE), "decision": reaction_gate.get("gate_decision")},
        },
    }
    evidence_path = QC / "exact_final_evidence_manifest.json"
    evidence_path.write_text(json.dumps(evidence_manifest, indent=2) + "\n")

    failed = [name for name, passed in gates.items() if not passed]
    report = {
        "schema_version": 1,
        "version": "capytech_v9_real_drop_qc_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact": rel(FINAL),
        "artifact_sha256": final_hash,
        "streams": {"video": video, "audio": audio},
        "duration_seconds": duration,
        "full_decode_stderr": decode.stderr,
        "detectors": {"black": black, "freeze": freeze, "silence": silence},
        "bottom_luma": luma,
        "loudness": {"integrated_lufs": integrated, "true_peak_dbtp": true_peak},
        "audio_boundary_slices": boundary_audio,
        "asr": asr,
        "evidence_manifest": rel(evidence_path),
        "exact_final_visual_review": assessment.get("status", "UNVERIFIED"),
        "human_visual_review": assessment.get("human_status", "UNVERIFIED"),
        "internal_transformative_checks_are_not_copyright_clearance": True,
        "publication_status": "NOT_UPLOADED",
        "virality_status": "VIRALITY_UNPROVEN",
        "gates": gates,
        "failed_gates": failed,
        "exact_final_pass": not failed,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "report": rel(REPORT),
                "artifact_sha256": final_hash,
                "exact_final_pass": not failed,
                "failed_gates": failed,
                "exact_final_visual_review": assessment.get("status", "UNVERIFIED"),
                "human_visual_review": assessment.get("human_status", "UNVERIFIED"),
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
