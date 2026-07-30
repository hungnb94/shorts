#!/usr/bin/env python3
"""Fail-closed exact-final QC for Capytech V8 Phone Drop."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "output/projects/capytech/final/2026-07-30-capytech_v8_phone_drop.mp4"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v8_phone_drop_storyboard.json"
RENDERER = ROOT / "pipeline/capytech/render_capytech_v8_phone_drop.py"
RENDER_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v8_phone_drop_work/render_manifest.json"
BENCHMARK_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v8_phone_drop_work/benchmark/benchmark_manifest.json"
FRAMES_DIR = ROOT / "output/projects/capytech/clips/capytech_v8_phone_drop_work/frames_H1"
HOOK_GATE = ROOT / "output/projects/capytech/analysis/v8_phone_drop_qc/hook_gate.json"
QC = ROOT / "output/projects/capytech/analysis/v8_phone_drop_qc"
EXPECTED_DURATION = 51.5
FPS = 30


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    return json.loads(run([
        "ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path),
    ]).stdout)


def ranges_cover_all(ranges: list[list[int]]) -> bool:
    covered: set[int] = set()
    for item in ranges:
        if not isinstance(item, list) or len(item) != 2:
            return False
        start, end = item
        if not isinstance(start, int) or not isinstance(end, int) or not 1 <= start <= end <= 1545:
            return False
        covered.update(range(start, end + 1))
    return covered == set(range(1, 1546))


def extract(video: Path, timestamp: float, output: Path, width=540, height=960) -> None:
    result = run([
        "ffmpeg", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video),
        "-frames:v", "1", "-vf", f"scale={width}:{height}:flags=lanczos", str(output),
    ], check=False)
    if result.returncode or not output.exists() or output.stat().st_size < 5_000:
        raise RuntimeError(f"exact-final frame extraction failed at {timestamp:.3f}s")


def sheet(items: list[tuple[str, float, Path]], output: Path, cols=6, thumb=(216, 384)) -> None:
    tile_w, tile_h = thumb[0] + 18, thumb[1] + 48
    rows = math.ceil(len(items) / cols)
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h), "#eef2f7")
    draw = ImageDraw.Draw(canvas)
    for index, (label, timestamp, path) in enumerate(items):
        image = Image.open(path).convert("RGB")
        image.thumbnail(thumb)
        x, y = (index % cols) * tile_w, (index // cols) * tile_h
        canvas.paste(image, (x + (tile_w - image.width) // 2, y + 42))
        draw.text((x + 6, y + 4), f"{label}\n{timestamp:.2f}s", fill="#111827")
    canvas.save(output, quality=94)


def parse_loudnorm(stderr: str) -> dict:
    start, end = stderr.rfind("{"), stderr.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("loudnorm JSON missing")
    return json.loads(stderr[start:end + 1])


def rate_is_30(value: str | None) -> bool:
    if not value or "/" not in value:
        return False
    numerator, denominator = (int(item) for item in value.split("/", 1))
    return denominator != 0 and abs(numerator / denominator - FPS) < 1e-9


def visual_diagnostics(video: Path) -> dict:
    """Diagnostics only. None of these measurements passes semantic gates."""
    import cv2
    import numpy as np

    capture = cv2.VideoCapture(str(video))
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    black_footer_samples = []
    clipping_samples = []
    for frame_index in range(0, total, max(1, round(FPS * 2))):
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = capture.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        black_footer_samples.append(float(gray[-96:, :].mean()))
        clipping_samples.append(float(np.mean((gray <= 1) | (gray >= 254))))
    capture.release()
    return {
        "bottom_96px_min_luma": min(black_footer_samples) if black_footer_samples else 0.0,
        "max_clipped_pixel_fraction": max(clipping_samples) if clipping_samples else 1.0,
        "note": "diagnostic only; generic pixels never satisfy semantic evidence",
    }


def evidence_contract(storyboard: dict) -> list[dict]:
    roles = ("pre_release", "airborne", "contact", "result", "reaction", "rail_update")
    records = []
    for round_data in storyboard["rounds"]:
        for role in roles:
            records.append({
                "round": round_data["id"],
                "role": role,
                "timestamp": float(round_data[role]),
                "expected_semantics": {
                    "pre_release": "hero phone visibly held/aligned above active height and plate",
                    "airborne": "hero phone visibly separated from paw and plate",
                    "contact": "hero phone visibly contacts the spring plate",
                    "result": "round-specific physical phone damage/result is readable",
                    "reaction": "round-specific capybara expression extreme visibly follows cause",
                    "rail_update": "correct compact result silhouette is visibly locked in rail",
                }[role],
            })
    for index, timestamp in enumerate(storyboard["rounds"][-1]["scale_states"], 1):
        records.append({
            "round": "100m", "role": f"scale_state_{index}", "timestamp": float(timestamp),
            "expected_semantics": f"falling hero phone has readable scale state {index}/3",
        })
    records.extend([
        {"round": "cta", "role": "like", "timestamp": 38.50,
         "expected_semantics": "LIKE card is readable while capy and phone remain airborne"},
        {"round": "cta", "role": "subscribe", "timestamp": 39.10,
         "expected_semantics": "SUB card is readable while capy and phone remain airborne"},
        {"round": "cta", "role": "comment", "timestamp": 39.70,
         "expected_semantics": "COMMENT card is readable while capy and phone remain airborne"},
        {"round": "watermark", "role": "route_1", "timestamp": 10.00,
         "expected_semantics": "moving watermark is visible in its first safe zone without collision"},
        {"round": "watermark", "role": "route_2", "timestamp": 25.00,
         "expected_semantics": "moving watermark is visible in its second safe zone without collision"},
        {"round": "watermark", "role": "route_3", "timestamp": 45.60,
         "expected_semantics": "moving watermark is visible in its third safe zone without collision"},
        {"round": "100m", "role": "plate_compression", "timestamp": 35.70,
         "expected_semantics": "plate visibly at maximum compression before rebound"},
        {"round": "100m", "role": "rebound", "timestamp": 36.50,
         "expected_semantics": "plate has rebounded and phone/debris launch upward"},
        {"round": "100m", "role": "final_damage", "timestamp": 44.80,
         "expected_semantics": "destroyed phone is readable before reset"},
        {"round": "100m", "role": "final_face", "timestamp": 45.60,
         "expected_semantics": "dazed final capybara reaction is readable before reset"},
        {"round": "loop", "role": "reset_release", "timestamp": 51.20,
         "expected_semantics": "phone, hand, camera and 1cm contract have reset; release begins"},
    ])
    return records


def main() -> int:
    if not FINAL.exists():
        raise FileNotFoundError(FINAL)
    if not STORYBOARD.exists():
        raise FileNotFoundError(STORYBOARD)
    QC.mkdir(parents=True, exist_ok=True)
    exact_dir = QC / "exact_final_evidence"
    pose_dir = QC / "pose_270x480"
    exact_dir.mkdir(parents=True, exist_ok=True)
    pose_dir.mkdir(parents=True, exist_ok=True)
    storyboard = json.loads(STORYBOARD.read_text())
    final_hash = sha256(FINAL)
    info = probe(FINAL)
    videos = [stream for stream in info["streams"] if stream.get("codec_type") == "video"]
    audios = [stream for stream in info["streams"] if stream.get("codec_type") == "audio"]
    if not videos or not audios:
        raise RuntimeError("missing video or audio stream")
    video, audio = videos[0], audios[0]
    duration = float(info["format"]["duration"])
    video_duration = float(video.get("duration", 0.0))
    audio_duration = float(audio.get("duration", 0.0))
    decoded_frames = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
    gates = {
        "duration_51_5": abs(duration - EXPECTED_DURATION) <= 0.10,
        "video_stream_duration_51_5": abs(video_duration - EXPECTED_DURATION) <= 0.10,
        "audio_stream_duration_51_5": abs(audio_duration - EXPECTED_DURATION) <= 0.10,
        "decoded_video_frames_1545": decoded_frames == 1545,
        "native_dimensions": video.get("width") == 1080 and video.get("height") == 1920,
        "h264": video.get("codec_name") == "h264",
        "yuv420p": video.get("pix_fmt") == "yuv420p",
        "cfr_30fps": rate_is_30(video.get("r_frame_rate")) and rate_is_30(video.get("avg_frame_rate")),
        "aac": audio.get("codec_name") == "aac",
        "audio_48khz": audio.get("sample_rate") == "48000",
        "audio_stereo": audio.get("channels") == 2,
    }

    decode = run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], check=False)
    gates["full_decode"] = decode.returncode == 0 and not decode.stderr.strip()
    detector = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
        "-vf", "blackdetect=d=0.20:pix_th=0.10,freezedetect=n=-60dB:d=1.0",
        "-af", "silencedetect=n=-48dB:d=0.75", "-f", "null", "-",
    ], check=False)
    detector_text = detector.stderr
    black_events = re.findall(r"black_start:[^\n]+", detector_text)
    freeze_events = re.findall(r"freeze_start:[^\n]+", detector_text)
    silence_events = re.findall(r"silence_start:[^\n]+", detector_text)
    gates["detector_execution"] = detector.returncode == 0
    gates["no_black_0_20s"] = detector.returncode == 0 and not black_events
    gates["no_freeze_1_0s"] = detector.returncode == 0 and not freeze_events
    gates["no_silence_0_75s"] = detector.returncode == 0 and not silence_events
    (QC / "detectors.log").write_text(detector_text)

    loud = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-",
    ], check=False)
    gates["loudness_measurement_execution"] = loud.returncode == 0
    loudness = parse_loudnorm(loud.stderr) if loud.returncode == 0 else {"input_i": "999", "input_tp": "999"}
    integrated, peak = float(loudness["input_i"]), float(loudness["input_tp"])
    gates["integrated_loudness"] = loud.returncode == 0 and -17.0 <= integrated <= -15.0
    gates["true_peak"] = loud.returncode == 0 and peak <= -1.5
    (QC / "loudness.json").write_text(json.dumps(loudness, indent=2) + "\n")

    contract = evidence_contract(storyboard)
    extracted: list[tuple[str, float, Path]] = []
    for item in contract:
        timestamp = item["timestamp"]
        if not 0 <= timestamp <= EXPECTED_DURATION:
            raise RuntimeError(f"semantic evidence timestamp out of range: {item}")
        name = f"{item['round']}_{item['role']}_{timestamp:05.2f}.jpg"
        output = exact_dir / name
        extract(FINAL, timestamp, output)
        item["file"] = str(output)
        extracted.append((f"{item['round']} {item['role']}", timestamp, output))
    sheet(extracted, QC / "semantic_evidence_sheet.jpg", cols=6)

    pose_times = {
        "ready_release": 0.05, "smug": 1.75, "wince_inspect": 8.30,
        "shock_brace": 17.40, "panic_airborne": 39.20,
    }
    pose_items = []
    for name, timestamp in pose_times.items():
        output = pose_dir / f"{name}_{timestamp:05.2f}.jpg"
        extract(FINAL, timestamp, output, width=270, height=480)
        pose_items.append((name, timestamp, output))
    sheet(pose_items, QC / "pose_family_sheet.jpg", cols=5, thumb=(270, 480))

    # Dense sequence sheets prove temporal properties that one still cannot:
    # cause/reaction order, CTA-on-motion, penetration, payoff and loop closure.
    sequence_specs = {
        "hook_0_3": (0.0, 3.0),
        "compression_rebound_35_38": (35.0, 38.0),
        "cta_airborne_38_40": (38.0, 40.0),
        "payoff_44_49": (44.0, 49.0),
        "loop_49_51_5": (49.0, 51.25),
    }
    sequence_sheets: list[Path] = []
    sequence_frames: list[Path] = []
    for name, (start_time, end_time) in sequence_specs.items():
        window_dir = QC / "sequence_windows" / name
        window_dir.mkdir(parents=True, exist_ok=True)
        frame_items = []
        timestamp = start_time
        while timestamp <= end_time + 1e-6:
            output = window_dir / f"{timestamp:05.2f}.jpg"
            extract(FINAL, timestamp, output, width=270, height=480)
            frame_items.append((name, timestamp, output))
            sequence_frames.append(output)
            timestamp += 0.25
        sheet_path = QC / f"{name}_sheet.jpg"
        sheet(frame_items, sheet_path, cols=6, thumb=(216, 384))
        sequence_sheets.append(sheet_path)

    evidence_payload_files = [Path(item["file"]) for item in contract] + [
        QC / "semantic_evidence_sheet.jpg", QC / "pose_family_sheet.jpg",
    ] + [item[2] for item in pose_items] + sequence_frames + sequence_sheets
    evidence_hashes = {
        str(path.relative_to(ROOT)): sha256(path) for path in evidence_payload_files
    }

    # A reviewer must assess the actual exact-final frames. The generated
    # template defaults to false, so absence or stale/partial review fails.
    assessment_path = QC / "semantic_assessment.json"
    existing_assessment = json.loads(assessment_path.read_text()) if assessment_path.exists() else {}
    if existing_assessment.get("artifact_sha256") != final_hash:
        assessment_path.write_text(json.dumps({
            "artifact_sha256": final_hash,
            "reviewer": "",
            "reviewed_at": "",
            "reviewed_exact_final": False,
            "evidence_sha256": evidence_hashes,
            "items": [
                {"round": item["round"], "role": item["role"], "timestamp": item["timestamp"],
                 "pass": False, "note": "UNREVIEWED"}
                for item in contract
            ],
            "sequence_windows": [
                {"name": name, "pass": False, "note": "UNREVIEWED"}
                for name in sequence_specs
            ],
            "pose_families_distinguishable_at_270x480": False,
            "eye_lines_target_phone": False,
            "no_paw_phone_penetration_over_2_frames": False,
            "reaction_follows_visible_cause": False,
            "no_footer_nonuniform_scale_or_clipping": False,
            "global_notes": {},
        }, indent=2) + "\n")
    assessment = json.loads(assessment_path.read_text())
    assessed = {(item.get("round"), item.get("role"), float(item.get("timestamp", -1))): item
                for item in assessment.get("items", [])}
    contract_keys = {(item["round"], item["role"], item["timestamp"]) for item in contract}
    gates["semantic_assessment_exact_hash"] = assessment.get("artifact_sha256") == final_hash
    gates["semantic_assessment_exact_final"] = assessment.get("reviewed_exact_final") is True
    gates["semantic_reviewer_identity"] = bool(assessment.get("reviewer") and assessment.get("reviewed_at"))
    gates["semantic_evidence_hashes"] = assessment.get("evidence_sha256") == evidence_hashes
    gates["semantic_evidence_all_pass"] = (
        set(assessed) == contract_keys
        and all(item.get("pass") is True for item in assessed.values())
        and all(len(str(item.get("note", ""))) >= 8 and item.get("note") != "UNREVIEWED"
                for item in assessed.values())
    )
    assessed_windows = {item.get("name"): item for item in assessment.get("sequence_windows", [])}
    gates["semantic_sequence_windows_all_pass"] = (
        set(assessed_windows) == set(sequence_specs)
        and all(item.get("pass") is True and len(str(item.get("note", ""))) >= 8
                and item.get("note") != "UNREVIEWED" for item in assessed_windows.values())
    )
    global_notes = assessment.get("global_notes", {})
    for field in (
        "pose_families_distinguishable_at_270x480", "eye_lines_target_phone",
        "no_paw_phone_penetration_over_2_frames", "reaction_follows_visible_cause",
        "no_footer_nonuniform_scale_or_clipping",
    ):
        gates[field] = assessment.get(field) is True and len(str(global_notes.get(field, ""))) >= 8

    render_manifest = json.loads(RENDER_MANIFEST.read_text()) if RENDER_MANIFEST.exists() else {}
    expected_cache_identity = {
        "renderer_sha256": sha256(RENDERER),
        "storyboard_sha256": sha256(STORYBOARD),
        "hook": "H1",
        "samples": 32,
        "blender_version": "5.2",
        "resolution": [1080, 1920],
        "fps": 30,
        "frame_count": 1545,
    }
    rendered_frame_names = {path.name for path in FRAMES_DIR.glob("frame_*.png")}
    expected_frame_names = {f"frame_{number:04d}.png" for number in range(1, 1546)}
    gates["render_manifest_present"] = RENDER_MANIFEST.exists()
    gates["render_manifest_exact_hash"] = render_manifest.get("final_sha256") == final_hash
    gates["storyboard_hash"] = render_manifest.get("storyboard_sha256") == sha256(STORYBOARD)
    gates["renderer_hash"] = render_manifest.get("renderer_sha256") == sha256(RENDERER)
    gates["cache_identity_exact"] = render_manifest.get("cache_identities", {}).get("H1") == expected_cache_identity
    gates["render_ranges_cover_1545"] = ranges_cover_all(
        render_manifest.get("completed_ranges", {}).get("H1", [])
    )
    gates["frame_cache_exact_1545"] = (
        rendered_frame_names == expected_frame_names
        and all((FRAMES_DIR / name).stat().st_size > 50_000 for name in expected_frame_names)
    )
    benchmark_manifest = json.loads(BENCHMARK_MANIFEST.read_text()) if BENCHMARK_MANIFEST.exists() else {}
    benchmark_hashes = benchmark_manifest.get("sha256", {})
    benchmark_paths = [
        ROOT / path
        for candidate in benchmark_manifest.get("candidates", [])
        for path in candidate.get("files", [])
    ]
    gates["benchmark_32_approved"] = (
        BENCHMARK_MANIFEST.exists()
        and benchmark_manifest.get("selected_samples") == 32
        and benchmark_manifest.get("selection_status") == "APPROVED_NATIVE_REVIEW"
        and benchmark_manifest.get("renderer_sha256") == sha256(RENDERER)
        and benchmark_manifest.get("storyboard_sha256") == sha256(STORYBOARD)
        and benchmark_manifest.get("blender_version") == "5.2"
        and bool(benchmark_paths)
        and all(path.exists() and benchmark_hashes.get(str(path.relative_to(ROOT))) == sha256(path)
                for path in benchmark_paths)
    )
    hook_gate = json.loads(HOOK_GATE.read_text()) if HOOK_GATE.exists() else {}
    hook_evidence = hook_gate.get("evidence", {})
    hook_paths = {
        "H1_video": ROOT / hook_evidence.get("H1_video", "missing"),
        "H1_sheet": ROOT / hook_evidence.get("H1_sheet", "missing"),
        "H3_video": ROOT / hook_evidence.get("H3_video", "missing"),
        "H3_sheet": ROOT / hook_evidence.get("H3_sheet", "missing"),
    }
    gates["hook_evidence_hash_bound"] = (
        HOOK_GATE.exists()
        and hook_evidence.get("renderer_sha256") == sha256(RENDERER)
        and hook_evidence.get("storyboard_sha256") == sha256(STORYBOARD)
        and hook_evidence.get("samples") == 32
        and all(path.exists() and hook_evidence.get("sha256", {}).get(name) == sha256(path)
                for name, path in hook_paths.items())
    )
    gates["native_blender_1080_contract"] = (
        render_manifest.get("blender_version") == "5.2" and video.get("width") == 1080
    )

    evidence_files = evidence_payload_files + [
        QC / "detectors.log", QC / "loudness.json", assessment_path,
    ]
    final_mtime = FINAL.stat().st_mtime
    gates["evidence_freshness"] = all(path.exists() and path.stat().st_mtime >= final_mtime for path in evidence_files)
    diagnostics = visual_diagnostics(FINAL)
    gates["no_black_footer_diagnostic"] = diagnostics["bottom_96px_min_luma"] >= 8.0
    gates["no_global_clipping_diagnostic"] = diagnostics["max_clipped_pixel_fraction"] <= 0.35

    evidence_manifest = {
        "artifact": str(FINAL), "artifact_sha256": final_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "semantic_contract": contract,
        "evidence_sha256": evidence_hashes,
        "sequence_windows": sequence_specs,
        "semantic_assessment": str(assessment_path),
    }
    evidence_manifest_path = QC / "evidence_manifest.json"
    evidence_manifest_path.write_text(json.dumps(evidence_manifest, indent=2) + "\n")
    gates["evidence_manifest_fresh"] = evidence_manifest_path.stat().st_mtime >= final_mtime

    # Human cold-viewer gate is deliberately reported, but does not falsify
    # objective local artifact QC.
    human_gate = {
        "status": "UNVERIFIED",
        "required_independent_cold_viewers": 5,
        "received": 0,
        "blocks_local_artifact_qc": False,
    }
    failed = [name for name, passed in gates.items() if not passed]
    report = {
        "version": "capytech_v8_phone_drop_qc_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact": str(FINAL),
        "sha256": final_hash,
        "duration_seconds": duration,
        "streams": {"video": video, "audio": audio},
        "loudness": {"integrated_lufs": integrated, "true_peak_dbtp": peak},
        "detectors": {"black": black_events, "freeze": freeze_events, "silence": silence_events},
        "visual_diagnostics": diagnostics,
        "asr": {"status": "NOT_APPLICABLE", "reason": "procedural nonverbal animation with no dialogue"},
        "human_cold_viewer_gate": human_gate,
        "publication_status": "NOT_UPLOADED",
        "virality_status": "VIRALITY_UNPROVEN",
        "gates": gates,
        "failed_gates": failed,
        "local_artifact_pass": not failed,
    }
    report_path = QC / "final_qc.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "report": str(report_path), "local_artifact_pass": not failed,
        "failed_gates": failed, "human_cold_viewer_gate": "UNVERIFIED",
        "sha256": final_hash,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
