#!/usr/bin/env python3
"""Fail-closed exact-final verifier for Capytech V10."""

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
WORK = ROOT / "output/projects/capytech/clips/capytech_v10_zack_reaction_explainer_work"
QC = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc"
FINAL = ROOT / "output/projects/capytech/final/2026-07-30-capytech_v10_zack_reaction_explainer.mp4"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v10_zack_reaction_explainer_storyboard.json"
GENERATOR = ROOT / "pipeline/capytech/generate_capytech_v10_zack_tts.py"
RENDERER = ROOT / "pipeline/capytech/render_capytech_v10_zack_reaction_explainer.py"
PREFLIGHT = ROOT / "pipeline/capytech/preflight_capytech_v10_zack_hook.py"
COMPOSITOR = ROOT / "pipeline/capytech/composite_capytech_v10_value_adds.py"
VERIFIER = Path(__file__).resolve()
PROFILE = ROOT / "data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json"
REFERENCE = PROFILE.parent / "reference.wav"
FONT = ROOT / "assets/fonts/Komika-Axis.ttf"
CALIBRATION = ROOT / "docs/verification/caption-calibration/caption-profile.json"
SYNTH_LOCK = ROOT / "spikes/001-english-tts-engine-bakeoff/requirements-mlx.txt"
SOURCE_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json"
SOURCE_USAGE = QC / "source_usage.json"
PEXELS_LICENSE = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/license.json"
PEXELS = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/36460444_aerial_city.mp4"
TTS_MANIFEST = WORK / "audio/tts_manifest.json"
RENDER_MANIFEST = WORK / "render_manifest.json"
FINAL_MANIFEST = WORK / "final_manifest.json"
REACTION_GATE = QC / "reaction_asset_manifest.json"
REPORT = QC / "exact_final_qc_report.json"
QC_CANDIDATE = QC / "qc_candidate.json"
EVIDENCE = QC / "exact_final_evidence_manifest.json"
VISUAL_ASSESSMENT = QC / "exact_final_visual_assessment.json"
PHONE_BAND_EVIDENCE = QC / "phone_band_bed_windows.json"
IMPLEMENTATION_REVIEW = QC / "codex_implementation_review.json"
FINAL_REVIEW = QC / "codex_exact_final_review.json"
STAGE0_PREVIEW = QC / "stage0/capytech_v10_zack_hook_0.0-5.0.mp4"
STAGE0_MANIFEST = QC / "stage0/hook_manifest.json"
STAGE0_REVIEW = QC / "stage0_external_naive_view.json"
ASR_PYTHON = Path("/usr/bin/python3")
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
FPS, DURATION = 30, 58.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def expected_synthesis_environment(profile_spec: dict[str, Any]) -> dict[str, Any]:
    expected = profile_spec["runtime"]["environments"]["synthesis"]
    approved_directory = (ROOT / "spikes/001-english-tts-engine-bakeoff").resolve()
    declared_relative = Path(expected["lock_file"])
    if declared_relative.is_absolute() or ".." in declared_relative.parts \
            or declared_relative.as_posix() != expected["lock_file"]:
        raise RuntimeError("Unsafe synthesis lock path in approved profile")
    approved_lock = (approved_directory / declared_relative).resolve()
    if approved_lock.parent != approved_directory or SYNTH_LOCK.resolve() != approved_lock:
        raise RuntimeError("Synthesis lock path differs from the approved profile path")
    lock_sha = sha256(SYNTH_LOCK)
    if lock_sha != expected["lock_sha256"]:
        raise RuntimeError("Synthesis lock SHA-256 differs from the approved profile pin")
    package_pattern = re.compile(r"^([A-Za-z0-9_.-]+)==([^ ;\\]+)")
    packages: dict[str, str] = {}
    for line in SYNTH_LOCK.read_text().splitlines():
        match = package_pattern.match(line)
        if match:
            name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
            packages[name] = match.group(2)

    return {
        "name": "synthesis", "python": expected["python"],
        "python_implementation": "cpython", "lock_file": expected["lock_file"],
        "lock_sha256": lock_sha, "packages": dict(sorted(packages.items())),
    }


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=check, text=True, capture_output=True)


def normalize(text: str) -> str:
    value = re.sub(r"['’]", "", text.lower())
    value = re.sub(r"\b1\s*,?\s*000\b", "one thousand", value)
    value = re.sub(r"\b300\b", "three hundred", value)
    value = re.sub(r"\b10\b", "ten", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def ordered_subsequence(expected: str, actual: str, ratio: float = 0.35) -> bool:
    wanted, got = normalize(expected).split(), normalize(actual).split()
    cursor = 0
    for token in wanted:
        try:
            cursor = got.index(token, cursor) + 1
        except ValueError:
            return False
    if len(got) - len(wanted) > max(3, math.ceil(len(wanted) * ratio)):
        return False
    return all(got.count(token) <= wanted.count(token) + 1 for token in set(wanted))


def asr_window(name: str, start: float, end: float) -> dict[str, Any]:
    directory = QC / "asr"
    directory.mkdir(parents=True, exist_ok=True)
    wav, record_path = directory / f"{name}.wav", directory / f"{name}.json"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start),
         "-t", str(end - start), "-i", str(FINAL), "-vn", "-ar", "16000", "-ac", "1",
         "-c:a", "pcm_s16le", str(wav)])
    code = ("import json,sys,mlx_whisper;"
            "r=mlx_whisper.transcribe(sys.argv[1],path_or_hf_repo=sys.argv[2],"
            "word_timestamps=True,language='en');print(json.dumps(r,ensure_ascii=False))")
    payload = json.loads(run([str(ASR_PYTHON), "-c", code, str(wav), ASR_MODEL]).stdout)
    words = [word for segment in payload.get("segments", []) for word in segment.get("words", [])
             if word.get("word")]
    reconstructed = "".join(str(word["word"]) for word in words).strip()
    record = {"window": [start, end], "wav": rel(wav), "wav_sha256": sha256(wav),
              "text": payload.get("text", reconstructed).strip(),
              "reconstructed_from_raw_tokens": reconstructed,
              "normalized": normalize(reconstructed), "words": words}
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


def extract_frame(name: str, at: float) -> Path:
    destination = QC / "exact_final_evidence" / name / f"{at:05.2f}.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.3f}",
         "-i", str(FINAL), "-frames:v", "1", "-vf", "scale=270:480:flags=lanczos", str(destination)])
    return destination


def make_sheet(name: str, start: float, end: float, step: float) -> tuple[Path, list[Path]]:
    frames, at = [], start
    while at < end - 1e-7:
        frames.append(extract_frame(name, at))
        at = round(at + step, 6)
    tile_w, tile_h, columns = 286, 525, 6
    sheet = Image.new("RGB", (tile_w * columns, tile_h * math.ceil(len(frames) / columns)), "#e5e7eb")
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        image = Image.open(frame).convert("RGB")
        x, y = index % columns * tile_w, index // columns * tile_h
        sheet.paste(image, (x + 8, y + 35))
        draw.text((x + 8, y + 8), frame.stem + "s", fill="#111827")
    output = QC / f"{name}_sheet.jpg"
    sheet.save(output, quality=94)
    return output, frames


def provenance_gates(final_hash: str) -> dict[str, bool]:
    tts, render, final, reaction = map(load, (TTS_MANIFEST, RENDER_MANIFEST, FINAL_MANIFEST, REACTION_GATE))
    profile_spec = load(PROFILE)
    continuous_bed = next(
        (asset for asset in render.get("audio_assets", [])
         if asset.get("id") == "procedural_continuous_bed"), {}
    )
    mechanism = render.get("mechanism_evidence", {})
    camera_motion = mechanism.get("continuous_camera_motion", {})
    motion_states = camera_motion.get("states", [])
    required_sfx = set(load(STORYBOARD)["audio_contract"]["required_asset_ids"])
    rendered_sfx = {asset.get("id") for asset in render.get("audio_assets", [])
                    if asset.get("id") != "procedural_continuous_bed"}
    files = {
        "storyboard": STORYBOARD, "generator": GENERATOR, "renderer": RENDERER,
        "preflight": PREFLIGHT, "compositor": COMPOSITOR, "verifier": VERIFIER, "profile": PROFILE,
        "reference": REFERENCE, "font": FONT, "calibration": CALIBRATION,
        "source_manifest": SOURCE_MANIFEST, "source_usage": SOURCE_USAGE,
        "reaction_gate": REACTION_GATE, "pexels_license": PEXELS_LICENSE, "pexels_asset": PEXELS,
    }
    gates = {f"current_{name}_exists": path.is_file() for name, path in files.items()}
    if not all(gates.values()):
        return gates
    expected = {
        "storyboard": final.get("storyboard_sha256"), "generator": final.get("tts_generator_sha256"),
        "renderer": final.get("renderer_sha256"), "compositor": final.get("compositor_sha256"),
        "profile": final.get("profile_sha256"), "font": final.get("font_sha256"),
        "calibration": final.get("caption_calibration_sha256"),
        "source_manifest": final.get("source_manifest_sha256"),
        "source_usage": final.get("source_usage_sha256"),
        "reaction_gate": final.get("reaction_gate_sha256"),
        "pexels_license": final.get("pexels_license_sha256"),
        "pexels_asset": final.get("pexels_asset_sha256"),
    }
    for name, digest in expected.items():
        gates[f"{name}_hash_bound"] = bool(digest) and sha256(files[name]) == digest
    gates.update({
        "final_artifact_hash_bound": final.get("artifact_sha256") == final_hash,
        "base_parent_hash_bound": final.get("base_artifact_sha256") == render.get("artifact_sha256"),
        "render_manifest_parent_hash_bound": final.get("render_manifest_sha256") == sha256(RENDER_MANIFEST),
        "tts_manifest_parent_hash_bound": render.get("tts_manifest_sha256") == sha256(TTS_MANIFEST),
        "reference_hash_bound": tts.get("profile", {}).get("reference_sha256") == sha256(REFERENCE),
        "zack_profile_id_exact": tts.get("profile", {}).get("id") == "ronald_wayne_zack_style_qwen",
        "zack_model_repo_exact": tts.get("model", {}).get("repo")
            == "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit",
        "zack_model_revision_exact": tts.get("model", {}).get("revision") == "34ff5318365b59cba9c03ff729f2eee0814caf72",
        "zack_weights_exact": tts.get("model", {}).get("weights") == {
            "model.safetensors": "b043693cb63f38f4e0ae5fe39a5cfdb466ef199dc5a767991a4a46235ac27e67",
            "speech_tokenizer/model.safetensors": "836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258",
        },
        "zack_generation_settings_exact": tts.get("generation_settings") == {
            "language": "English", "temperature": 0.7, "max_tokens": 768,
            "top_k": 30, "top_p": 0.9, "repetition_penalty": 1.5,
        },
        "rubberband_exact": tts.get("fitting_settings", {}).get("version") == "Rubber Band R3 4.0.0",
        "rubberband_cli_4_0_0": tts.get("fitting_settings", {}).get("cli_version") == "4.0.0"
            and tts.get("fitting_settings", {}).get("engine_label") == "Rubber Band R3"
            and tts.get("fitting_settings", {}).get("mode") == "R3_FINE"
            and tts.get("fitting_settings", {}).get("command_flag") == "--fine",
        "per_line_r3_fine_or_exact_bypass": all(
            line.get("tempo_engine_observed")
                == ("R3_FINE" if float(line.get("measured_tempo", 99)) > 1.0 + 1e-6
                    else "BYPASS_TEMPO_1_0")
            for line in tts["lines"]
        ),
        "v10_reviewed_ffmpeg_runtime_exact": tts.get("runtime", {}).get("policy")
            == "V10_REVIEWED_FFMPEG_RUNTIME_OVERRIDE_PROFILE_UNCHANGED"
            and tts.get("runtime", {}).get("profile_expected")
                == profile_spec["runtime"]["repeatability_fingerprints"]
            and tts.get("runtime", {}).get("actual", {}).get("ffmpeg") == {
                "version_line": "ffmpeg version 7.1.1 Copyright (c) 2000-2025 the FFmpeg developers",
                "version_output_sha256": "88b12a030360dd4614c0e3999e442dd5cfa63c6df2b7b8dc2f23f56a40399ff9",
            }
            and tts.get("runtime", {}).get("actual", {}).get("platform")
                == tts.get("runtime", {}).get("profile_expected", {}).get("platform")
            and tts.get("runtime", {}).get("synthesis_environment")
                == expected_synthesis_environment(profile_spec),
        "tempo_at_or_below_1_42": all(float(line.get("measured_tempo", 99)) <= 1.42 for line in tts["lines"]),
        "native_reaction_assets_only": reaction.get("generation") == "native_1080x1920_procedural_no_proxy_upscale"
            and all(asset.get("canvas") == [1080, 1920] for asset in reaction.get("assets", [])),
        "signature_recoil_asset_delta": float(reaction.get("signature_body_center_recoil_pixels", 0)) >= 90,
        "signature_feet_stable": float(reaction.get("signature_foot_reference_max_drift_pixels", 999)) <= 1,
        "final_transformed_landmarks_recorded": bool(reaction.get("final_overlay_geometry"))
            and all(item.get("overlay_xy") == [0, 0] and item.get("final_landmarks")
                    for item in reaction.get("final_overlay_geometry", [])),
        "reaction_evidence_safe_regions_have_zero_alpha_overlap":
            bool(reaction.get("evidence_safe_region_alpha_overlap_pixels"))
            and all(int(value) == 0 for value in
                    reaction.get("evidence_safe_region_alpha_overlap_pixels", {}).values()),
        "audio_assets_provenance_bound": bool(render.get("audio_assets"))
            and final.get("audio_assets") == render.get("audio_assets"),
        "implementation_review_parent_bound":
            final.get("implementation_review_sha256") == render.get("implementation_review_sha256"),
        "caption_profile_values_applied":
            render.get("caption_profile_applied") == load(CALIBRATION).get("ffmpeg_profile"),
        "mechanism_has_locked_real_frames_tracker_annotation_and_two_scale_changes":
            mechanism.get("layout")
                == "locked_real_concrete_frame_over_locked_real_red_dirt_frame"
            and bool(mechanism.get("moving_tracker"))
            and bool(mechanism.get("stopping_distance_annotation"))
            and len(mechanism.get("scale_states", [])) == 3
            and camera_motion.get("mode") == "one_way_evidence_pan"
            and camera_motion.get("requested_concrete_delta_pixels") == [45, 18]
            and camera_motion.get("requested_red_dirt_delta_pixels") == [60, 18]
            and camera_motion.get("reset_only_at_information_scale_change") is True
            and len(motion_states) == 3
            and all(
                state.get("concrete_effective_delta_pixels") == [45, 18]
                and state.get("red_dirt_effective_delta_pixels") == [60, 18]
                and int(state.get("concrete_scaled_canvas", [0, 0])[0]) >= 1125
                and int(state.get("concrete_scaled_canvas", [0, 0])[1]) >= 978
                and int(state.get("red_dirt_scaled_canvas", [0, 0])[0]) >= 1140
                and int(state.get("red_dirt_scaled_canvas", [0, 0])[1]) >= 978
                for state in motion_states
            )
            and [
                {"window": state.get("window"), "scale": state.get("scale")}
                for state in motion_states
            ] == mechanism.get("scale_states"),
        "phone_band_harmonic_pad_provenance_exact":
            continuous_bed.get("provenance")
                == "original_procedural_phone_band_harmonic_pad_no_external_asset"
            and continuous_bed.get("generator") == "ffmpeg lavfi 196_294_392hz_harmonic_pad"
            and continuous_bed.get("phone_translation_band_hz") == [150, 2000]
            and continuous_bed.get("window") == [0.0, DURATION],
        "continuous_bed_and_required_event_sfx_present":
            any(asset.get("id") == "procedural_continuous_bed"
                for asset in render.get("audio_assets", []))
            and rendered_sfx == required_sfx,
    })
    return gates


def review_gate(path: Path, expected: dict[str, str], allowed_status: set[str]) -> tuple[bool, str]:
    if not path.is_file():
        return False, "UNVERIFIED"
    record = load(path)
    current = record.get("bindings", {})
    if any(current.get(key) != value for key, value in expected.items()):
        return False, "STALE"
    return (record.get("status") in allowed_status and bool(record.get("reviewer"))
            and bool(record.get("reviewed_at_utc"))
            and not record.get("unresolved_actionable_findings")), record.get("status", "UNVERIFIED")


def stage0_review_gate() -> tuple[bool, str]:
    """Independently enforce the renderer's current Stage-0 review contract."""
    if not all(path.is_file() for path in (STAGE0_PREVIEW, STAGE0_MANIFEST, STAGE0_REVIEW)):
        return False, "UNVERIFIED"
    record = load(STAGE0_REVIEW)
    expected = {
        "hook_preview": sha256(STAGE0_PREVIEW),
        "hook_manifest": sha256(STAGE0_MANIFEST),
        "storyboard": sha256(STORYBOARD),
        "tts_manifest": sha256(TTS_MANIFEST),
        "renderer": sha256(RENDERER),
        "preflight": sha256(PREFLIGHT),
    }
    required_assessment = {
        "human_face_at_frame0",
        "frame0_human_expression_is_surprised",
        "caption_visible_by_0_2s",
        "ordered_300ft_split_then_real_1000ft_scale_then_powered_display",
        "same_phone_ambiguity_rejected",
        "curiosity_open_question",
        "no_collision",
        "no_black_frames",
        "no_crop_failure",
    }
    try:
        reviewed_at = datetime.fromisoformat(
            str(record.get("reviewed_at_utc", "")).replace("Z", "+00:00"))
    except ValueError:
        return False, "INVALID_UTC"
    assessment = record.get("assessment", {})
    passed = record.get("status") == "PASS_STAGE0_EXTERNAL_NAIVE_VIEW" \
        and bool(record.get("reviewer")) and bool(record.get("reviewer_type")) \
        and reviewed_at.utcoffset() == timezone.utc.utcoffset(reviewed_at) \
        and record.get("bindings") == expected \
        and set(assessment) == required_assessment and all(assessment.values())
    return passed, record.get("status", "UNVERIFIED")


def main() -> int:
    required = [FINAL, STORYBOARD, GENERATOR, RENDERER, PREFLIGHT, COMPOSITOR, PROFILE, REFERENCE, FONT,
                CALIBRATION, SOURCE_MANIFEST, SOURCE_USAGE, PEXELS_LICENSE, PEXELS,
                TTS_MANIFEST, RENDER_MANIFEST, FINAL_MANIFEST, REACTION_GATE,
                STAGE0_PREVIEW, STAGE0_MANIFEST, STAGE0_REVIEW, ASR_PYTHON]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    QC.mkdir(parents=True, exist_ok=True)
    final_hash = sha256(FINAL)
    info = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams",
                           "-show_format", "-of", "json", str(FINAL)]).stdout)
    video = next(stream for stream in info["streams"] if stream.get("codec_type") == "video")
    audio = next(stream for stream in info["streams"] if stream.get("codec_type") == "audio")
    duration = float(info["format"]["duration"])
    frames = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
    gates = {
        "duration_58_seconds": abs(duration - DURATION) <= 0.1,
        "duration_50_to_75_seconds": 50 <= duration <= 75,
        "video_1080x1920": (video.get("width"), video.get("height")) == (1080, 1920),
        "h264_high_yuv420p": video.get("codec_name") == "h264"
            and video.get("profile") == "High" and video.get("pix_fmt") == "yuv420p",
        "cfr_30fps": video.get("r_frame_rate") in {"30/1", "60/2"}
            and video.get("avg_frame_rate") in {"30/1", "60/2"},
        "exact_frame_count": frames == 1740,
        "aac_48khz_stereo": audio.get("codec_name") == "aac"
            and audio.get("sample_rate") == "48000" and audio.get("channels") == 2,
    }
    gates.update(provenance_gates(final_hash))
    decode = run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], check=False)
    gates["full_decode"] = decode.returncode == 0 and not decode.stderr.strip()
    detector_specs = {
        "black": ["-vf", "blackdetect=d=0.2:pix_th=0.1"],
        "freeze": ["-vf", "freezedetect=n=-60dB:d=1.0"],
        "silence": ["-af", "silencedetect=n=-48dB:d=0.75"],
    }
    detector_records = {}
    for name, arguments in detector_specs.items():
        command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
                   *arguments, "-f", "null", "-"]
        process = run(command, check=False)
        raw_log = QC / f"detector_{name}.log"
        raw_log.write_text(process.stderr)
        semantic_events = re.findall(
            r"(?:black|freeze|silence)_(?:start|end|duration):\s*-?\d+(?:\.\d+)?",
            process.stderr,
        )
        detector_records[name] = {
            "command": command,
            "returncode": process.returncode,
            "semantic_events": semantic_events,
            "raw_log": rel(raw_log),
        }
        gates[f"{name}_detector_completed"] = process.returncode == 0
        gates[f"no_unexplained_{name}"] = process.returncode == 0 and not semantic_events
    loud_command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL), "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"]
    loud = run(loud_command, check=False)
    match = re.search(r"\{\s*\"input_i\".*?\}", loud.stderr, re.S)
    loudness = json.loads(match.group(0)) if match else {}
    expected_loudness = {"input_i", "input_tp", "input_lra", "input_thresh", "target_offset"}
    finite_loudness = expected_loudness <= set(loudness) and all(
        math.isfinite(float(loudness[key])) for key in expected_loudness)
    loudness_record = {"command": loud_command, "returncode": loud.returncode,
                       "stderr": loud.stderr, "measurement": loudness}
    (QC / "loudness.json").write_text(json.dumps(loudness_record, indent=2) + "\n")
    gates["loudness_measurement_completed"] = loud.returncode == 0 and finite_loudness
    gates["integrated_loudness"] = gates["loudness_measurement_completed"] \
        and -17 <= float(loudness["input_i"]) <= -15
    gates["true_peak"] = gates["loudness_measurement_completed"] \
        and float(loudness["input_tp"]) <= -1.5

    # Measure exact-final narration gaps in a phone-translatable band.  This
    # proves that the bed is both present and bounded; it cannot pass merely by
    # hiding sub-bass below typical phone-speaker response.
    phone_band_windows = {
        "post_ten_pre_rigid": [14.2, 18.8],
        "post_split_pre_shock": [27.0, 28.4],
        "post_shock_pre_thousand": [31.6, 33.4],
    }
    phone_band_records: dict[str, Any] = {}
    phone_band_completed = True
    phone_band_bounded = True
    for name, (start, end) in phone_band_windows.items():
        command = [
            "ffmpeg", "-hide_banner", "-nostats", "-ss", str(start),
            "-t", str(end - start), "-i", str(FINAL), "-vn", "-af",
            "highpass=f=150,lowpass=f=2000,volumedetect", "-f", "null", "-",
        ]
        process = run(command, check=False)
        mean_match = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", process.stderr)
        max_match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", process.stderr)
        mean_db = float(mean_match.group(1)) if mean_match else None
        max_db = float(max_match.group(1)) if max_match else None
        completed = process.returncode == 0 and mean_db is not None and max_db is not None
        if completed:
            assert mean_db is not None and max_db is not None
            bounded = -48.0 <= mean_db <= -32.0 and -45.0 <= max_db <= -24.0
        else:
            bounded = False
        phone_band_completed = phone_band_completed and completed
        phone_band_bounded = phone_band_bounded and bounded
        normalized_measurement = {
            "returncode": process.returncode,
            "mean_volume_db": mean_db,
            "max_volume_db": max_db,
        }
        phone_band_records[name] = {
            "window": [start, end],
            "command": command,
            **normalized_measurement,
            "bounded": bounded,
            "normalized_measurement_sha256": hashlib.sha256(
                json.dumps(normalized_measurement, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        }
    phone_band_evidence = {
        "schema_version": 1, "artifact": rel(FINAL), "artifact_sha256": final_hash,
        "translation_band_hz": [150, 2000], "acceptable_mean_db": [-48.0, -32.0],
        "acceptable_max_db": [-45.0, -24.0], "windows": phone_band_records,
    }
    PHONE_BAND_EVIDENCE.write_text(json.dumps(phone_band_evidence, indent=2) + "\n")
    gates["phone_band_bed_measurement_completed"] = phone_band_completed
    gates["phone_band_bed_present_and_not_overpowering"] = phone_band_completed and phone_band_bounded

    storyboard = load(STORYBOARD)
    windows = storyboard["verification"]["asr_windows"]
    asr = {name: asr_window(name, *window) for name, window in windows.items()}
    lines = {line["id"]: line for line in storyboard["tts_contract"]["lines"]}
    body_expected = " ".join(lines[item]["text"] for item in
                             ("waist", "ten", "rigid", "three_hundred", "shock", "thousand_setup"))
    gates.update({
        "hook_asr_ordered": ordered_subsequence(lines["hook"]["text"], asr["hook"]["text"]),
        "body_asr_ordered": ordered_subsequence(body_expected, asr["body"]["text"]),
        "cta_asr_ordered": ordered_subsequence(lines["cta"]["text"], asr["cta"]["text"]),
        "mechanism_asr_ordered": ordered_subsequence(lines["mechanism"]["text"], asr["mechanism"]["text"]),
        "payoff_asr_ordered": ordered_subsequence(lines["payoff"]["text"], asr["payoff"]["text"]),
        "quote_isolated_exact": ordered_subsequence("It is on! That's unreal!", asr["quote_isolation"]["text"], 0.5)
            and not ordered_subsequence(lines["payoff"]["text"], asr["quote_isolation"]["text"]),
        "tail_asr_ordered": ordered_subsequence(lines["loop"]["text"], asr["tail"]["text"]),
        "full_allowlist_ordered": ordered_subsequence(
            " ".join(line["text"] for line in storyboard["tts_contract"]["lines"][:-1])
            + " It is on! That's unreal! " + lines["loop"]["text"], asr["full"]["text"], 0.45),
    })
    tts = load(TTS_MANIFEST)
    hook_line = next(line for line in tts["lines"] if line["id"] == "hook")
    caption = next(item for item in load(RENDER_MANIFEST)["caption_bursts"] if item["line_id"] == "hook")
    gates["hook_caption_matches_audible_onset"] = (
        abs(float(caption["start"]) - float(hook_line["speech_onset_seconds_absolute"])) <= 0.2
    )
    gates["no_narration_overlap"] = all(
        float(left["speech_end_seconds_absolute"]) <= float(right["speech_onset_seconds_absolute"])
        for left, right in zip(tts["lines"], tts["lines"][1:])
    )
    gates["payoff_last_word_by_52_35"] = float(next(line for line in tts["lines"] if line["id"] == "payoff")
                                                ["speech_end_seconds_absolute"]) <= 52.35
    gates["cta_last_word_by_41_7"] = float(next(line for line in tts["lines"] if line["id"] == "cta")
                                           ["speech_end_seconds_absolute"]) <= 41.7
    gates["loop_last_word_by_57_75"] = float(next(line for line in tts["lines"] if line["id"] == "loop")
                                             ["speech_end_seconds_absolute"]) <= 57.75

    sheet_specs = {
        "caption_onset": (0.0, 0.5, 0.1), "hook": (0.0, 3.0, 0.2),
        "baseline_confidence": (7.5, 10.0, 0.25), "shielding_concern": (15.5, 19.0, 0.25),
        "split_proof_before_reaction": (29.0, 30.0, 0.1),
        "signature_eyes_mouth_paws_recoil": (29.5, 31.1, 0.1),
        "signature_full_coverage": (29.5, 33.5, 0.25),
        "cta_sequence_and_source_type": (38.0, 42.0, 0.2),
        "mechanism_evidence_order": (42.0, 49.0, 0.25),
        "powered_disbelief": (49.0, 52.6, 0.2),
        "quote_isolation": (52.3, 56.1, 0.2), "loop": (56.0, 58.0, 0.1),
    }
    sheets, frame_paths = [], []
    for name, (start, end, step) in sheet_specs.items():
        sheet, extracted = make_sheet(name, start, end, step)
        sheets.append(sheet)
        frame_paths.extend(extracted)
    evidence_hashes = {rel(path): sha256(path) for path in sheets + frame_paths}
    required_visual = {
        "caption_visible_by_0_2", "caption_bursts_2_to_5_words",
        "one_emphasized_keyword_per_caption", "caption_center_55_to_65_percent",
        "frame_zero_has_moving_expressive_human_source", "four_hook_beats_under_0_9_seconds",
        "split_proof_readable_by_1_4", "baseline_confidence_identifiable",
        "shielding_concern_identifiable", "signature_shock_identifiable",
        "powered_disbelief_identifiable", "powered_eye_pop_identifiable",
        "powered_recoil_identifiable", "powered_feet_reference_stable",
        "split_evidence_readable_before_reaction",
        "signature_height_65_to_75_percent", "signature_eyes_readable",
        "signature_mouth_readable", "signature_left_paw_readable",
        "signature_right_paw_readable", "signature_body_center_recoils_after_proof",
        "signature_pose_silhouette_changes_not_camera_shake",
        "signature_evidence_remains_unobstructed", "no_long_lived_panic_sticker",
        "pexels_labeled_illustration_entire_38_to_40", "real_source_action_40_to_42",
        "cta_like_subscribe_comment_enter_sequentially", "different_tests_visible",
        "possible_mechanism_visible", "disclaimer_readable_entire_42_to_49",
        "mechanism_evidence_order_surface_then_stopping_distance_then_confounders",
        "two_camera_scale_changes_42_to_49", "powered_display_unobstructed",
        "height_alone_non_ranking_card", "moving_watermark_changes_position",
        "citations_readable", "early_and_event_bound_sfx", "information_progression",
    }
    assessment = load(VISUAL_ASSESSMENT) if VISUAL_ASSESSMENT.is_file() else {}
    if assessment.get("artifact_sha256") != final_hash or assessment.get("evidence_sha256") != evidence_hashes:
        assessment = {"artifact_sha256": final_hash, "evidence_sha256": evidence_hashes,
                      "status": "UNVERIFIED", "reviewer": "", "reviewer_type": "",
                      "reviewed_at_utc": "", "human_cold_viewer_status": "UNVERIFIED",
                      "checks": {name: False for name in sorted(required_visual)}, "notes": {}}
        VISUAL_ASSESSMENT.write_text(json.dumps(assessment, indent=2) + "\n")
    checks = assessment.get("checks", {})
    gates["visual_assessment_hash_bound"] = assessment.get("artifact_sha256") == final_hash \
        and assessment.get("evidence_sha256") == evidence_hashes
    gates["visual_assessment_granular_and_passed"] = set(checks) == required_visual \
        and all(checks.values()) and assessment.get("status") in {"VERIFIED", "VERIFIED_MACHINE_PROXY"} \
        and assessment.get("reviewer_type") in {"human", "machine_proxy"}
    gates["human_cold_viewer_not_falsely_claimed"] = assessment.get("human_cold_viewer_status") in \
        {"UNVERIFIED", "VERIFIED_BY_INDEPENDENT_HUMAN"}

    implementation_bindings = {name: sha256(path) for name, path in
                               {"storyboard": STORYBOARD, "generator": GENERATOR, "renderer": RENDERER,
                                "preflight": PREFLIGHT, "compositor": COMPOSITOR,
                                "verifier": VERIFIER}.items()}
    implementation_ok, implementation_status = review_gate(
        IMPLEMENTATION_REVIEW, implementation_bindings, {"PASS_ACTIONABLE_FINDINGS_APPLIED"})
    gates["codex_implementation_review_current"] = implementation_ok
    stage0_ok, stage0_status = stage0_review_gate()
    gates["stage0_external_naive_view_current_and_passed"] = stage0_ok

    usage = load(SOURCE_USAGE)
    gates["all_retained_source_clips_under_15s"] = all(float(item["final_duration"]) < 15
                                                        for item in usage["occurrences"])
    source_durations: dict[str, float] = {}
    for source in load(SOURCE_MANIFEST)["sources"]:
        source_durations[source["youtube_id"]] = float(source["source_duration_seconds"])
    gates["each_source_aggregate_below_50_percent"] = all(
        float(seconds) <= source_durations[youtube_id] * 0.5
        for youtube_id, seconds in usage.get("aggregate_youtube_usage_seconds", {}).items()
    ) and bool(usage.get("aggregate_youtube_usage_seconds"))
    gates["source_audio_muted_except_quote"] = usage.get("all_visual_source_audio_muted") is True \
        and usage.get("only_approved_quote", {}).get("window") == [52.6, 55.9]
    gates["at_least_two_post_render_value_adds"] = len(load(FINAL_MANIFEST).get("value_adds", [])) >= 2
    gates["publication_not_uploaded"] = load(FINAL_MANIFEST).get("publication_status") == "NOT_UPLOADED"
    gates["virality_unproven"] = load(FINAL_MANIFEST).get("virality_status") == "VIRALITY_UNPROVEN"

    evidence_manifest = {"schema_version": 3, "artifact": rel(FINAL), "artifact_sha256": final_hash,
                         "sheets": [rel(path) for path in sheets], "evidence_sha256": evidence_hashes,
                         "asr": {name: {"path": rel(QC / "asr" / f"{name}.json"),
                                        "sha256": sha256(QC / "asr" / f"{name}.json")} for name in asr},
                         "visual_assessment": rel(VISUAL_ASSESSMENT),
                         "visual_assessment_sha256": sha256(VISUAL_ASSESSMENT)}
    EVIDENCE.write_text(json.dumps(evidence_manifest, indent=2) + "\n")
    # This canonical payload is immutable for a given artifact and evidence set.
    # It intentionally excludes timestamps, report text, and review status.
    candidate = {
        "schema_version": 1,
        "artifact": rel(FINAL),
        "artifact_sha256": final_hash,
        "implementation_bindings": implementation_bindings,
        "provenance": {
            "tts_manifest": sha256(TTS_MANIFEST),
            "render_manifest": sha256(RENDER_MANIFEST),
            "final_manifest": sha256(FINAL_MANIFEST),
            "evidence_manifest": sha256(EVIDENCE),
            "implementation_review": sha256(IMPLEMENTATION_REVIEW),
            "audio_assets": load(FINAL_MANIFEST).get("audio_asset_dag_sha256"),
            "phone_band_bed_evidence": sha256(PHONE_BAND_EVIDENCE),
        },
        "asr_evidence_sha256": hashlib.sha256(
            json.dumps(asr, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "visual_evidence_sha256": hashlib.sha256(
            json.dumps(evidence_hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "detectors": detector_records,
        "loudness": {"command": loud_command, "returncode": loud.returncode,
                     "measurement": loudness},
        "gates_before_exact_final_review": gates,
    }
    QC_CANDIDATE.write_text(json.dumps(candidate, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False) + "\n")
    final_bindings = {"qc_candidate": sha256(QC_CANDIDATE)}
    final_ok, final_status = review_gate(
        FINAL_REVIEW, final_bindings, {"PASS_ACTIONABLE_FINDINGS_APPLIED"})
    gates["codex_exact_final_review_current"] = final_ok
    failed = sorted(name for name, passed in gates.items() if not passed)
    report = {"schema_version": 2, "version": "capytech_v10_zack_reaction_explainer_qc_v1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "artifact": rel(FINAL), "artifact_sha256": final_hash,
              "provenance_dag": {"tts_manifest": sha256(TTS_MANIFEST),
                                 "render_manifest": sha256(RENDER_MANIFEST),
                                 "final_manifest": sha256(FINAL_MANIFEST),
                                 "evidence_manifest": sha256(EVIDENCE),
                                 "qc_candidate": sha256(QC_CANDIDATE),
                                 "implementation_review": sha256(IMPLEMENTATION_REVIEW),
                                 "phone_band_bed_evidence": sha256(PHONE_BAND_EVIDENCE),
                                 "exact_final_review_packet":
                                     sha256(FINAL_REVIEW) if FINAL_REVIEW.is_file() else "MISSING",
                                 "audio_assets": load(FINAL_MANIFEST).get("audio_asset_dag_sha256")},
              "asr": asr, "implementation_review_status": implementation_status,
              "stage0_external_naive_view_status": stage0_status,
              "exact_final_review_status": final_status,
              "human_cold_viewer_status": assessment.get("human_cold_viewer_status", "UNVERIFIED"),
              "publication_status": "NOT_UPLOADED", "virality_status": "VIRALITY_UNPROVEN",
              "gates": gates, "failed_gates": failed, "exact_final_pass": not failed}
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"report": rel(REPORT), "exact_final_pass": not failed,
                      "failed_gates": failed}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
