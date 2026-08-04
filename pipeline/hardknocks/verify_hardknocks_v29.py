#!/usr/bin/env python3
"""Exact-final automated media verification for HardKnocks V29."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
FINAL = PROJECT / "final" / "2026-08-04-hardknocks_v29_supply_chain_trap.mp4"
SOURCE = ROOT / "output" / "projects" / "dangote-supply-chain" / "source" / "master" / "jVs4NBoHZic-source-master.mp4"
WORK = PROJECT / "clips" / "v29_supply_chain_trap_work"
TIMELINE = WORK / "timeline.json"
ASSET_MANIFEST = WORK / "asset-manifest.json"
TIMED_SFX = WORK / "audio" / "sfx" / "timed_full.wav"
MUSIC_BED = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22" / "restrained_finance_bed.wav"
CHECKS = WORK / "checks"
FRAMES = CHECKS / "sampled_frames"
HOOK_FRAMES = CHECKS / "hook_motion_frames"
MIDPOINT_FRAMES = CHECKS / "segment_midpoints"
BOUNDARY_FRAMES = CHECKS / "boundary_frames"
SOURCE_SWEEP_FRAMES = CHECKS / "source_sweep"
CRITICAL_FRAMES = CHECKS / "critical_frames"
ASR_JSON = CHECKS / "final_asr.json"
SFX_AUDIT = CHECKS / "sfx-event-audit.json"
FINAL_AUDIO = CHECKS / "final_audio.wav"
WHISPER_PYTHON = ROOT / "spikes" / "001-english-tts-engine-bakeoff" / ".venv-asr" / "bin" / "python"
TRANSCRIBE = ROOT / "pipeline" / "tools" / "transcribe.py"
ASR_MODEL = "mlx-community/whisper-small.en-mlx"

RENDERER_PATH = ROOT / "pipeline" / "hardknocks" / "render_hardknocks_v29_supply_chain_trap.py"
_spec = importlib.util.spec_from_file_location("render_hardknocks_v29_supply_chain_trap", RENDERER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to import {RENDERER_PATH}")
renderer = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = renderer
_spec.loader.exec_module(renderer)

EVENTS = (
    (0.04, "hook"),
    (1.50, "refine_gap"),
    (3.00, "export"),
    (4.50, "import"),
    (6.00, "import_cost"),
    (7.50, "question"),
    (12.00, "decision"),
    (18.00, "mechanism"),
    (22.50, "timing"),
    (24.00, "quality"),
    (25.50, "cost"),
    (27.00, "capacity"),
    (33.00, "upstream"),
    (37.80, "cta_like"),
    (38.70, "cta_sub"),
    (39.60, "cta_comment"),
    (42.00, "allocation"),
    (48.00, "cargo"),
    (54.00, "payoff"),
    (60.00, "loop"),
)


def cmd(args: list[str | Path], *, check: bool = True) -> str:
    result = subprocess.run([str(item) for item in args], text=True, capture_output=True, cwd=ROOT)
    if check and result.returncode != 0:
        raise RuntimeError((result.stdout or "") + (result.stderr or ""))
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path]).strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9$% ]+", " ", text.lower())).strip()


def extract_frame(timestamp: float, output: Path, *, width: int = 270, height: int = 480) -> None:
    cmd([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.3f}", "-i", FINAL,
        "-frames:v", "1", "-vf", f"scale={width}:{height}", output,
    ])


def make_contact_sheet(pattern: str, output: Path, *, cols: int, rows: int, width: int = 216, height: int = 384) -> None:
    cmd([
        "ffmpeg", "-y", "-v", "error", "-pattern_type", "glob", "-i", pattern,
        "-vf", f"scale={width}:{height},tile={cols}x{rows}:padding=4:margin=4:color=0x081120",
        "-frames:v", "1", output,
    ])


def word_window(asr: dict, start: float, end: float) -> str:
    words = [
        str(word.get("word", ""))
        for segment in asr.get("segments", [])
        for word in segment.get("words", [])
        if float(word.get("start", -1)) < end and float(word.get("end", -1)) > start
    ]
    return normalize_text("".join(words))


def skin_ratio(path: Path) -> float:
    array = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
    red, green, blue = array[..., 0], array[..., 1], array[..., 2]
    mask = (
        (red > 95) & (green > 40) & (blue > 20) & (red > green) & (red > blue)
        & ((red - green) > 15) & ((array.max(axis=2) - array.min(axis=2)) > 15)
    )
    return float(mask.mean())


def read_pcm(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        rate = handle.getframerate()
        width = handle.getsampwidth()
        frames = handle.readframes(handle.getnframes())
    if width != 2:
        raise RuntimeError(f"Expected 16-bit PCM: {path}")
    samples = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return rate, samples


def dbfs_window(samples: np.ndarray, rate: int, start: float, seconds: float = 0.25) -> float:
    left = max(0, round(start * rate))
    right = min(len(samples), round((start + seconds) * rate))
    if right <= left:
        return -180.0
    rms = float(np.sqrt(np.mean(np.square(samples[left:right]))))
    return 20 * math.log10(max(rms, 1e-9))


def audit_sfx(final_hash: str) -> dict:
    cmd(["ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vn", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", FINAL_AUDIO])
    sfx_rate, sfx = read_pcm(TIMED_SFX)
    bed_rate, bed = read_pcm(MUSIC_BED)
    final_rate, final_audio = read_pcm(FINAL_AUDIO)
    rows = []
    for at, name in EVENTS:
        sfx_db = dbfs_window(sfx, sfx_rate, at)
        pre_db = dbfs_window(sfx, sfx_rate, max(0, at - 0.5))
        bed_db = dbfs_window(bed, bed_rate, at) + 20 * math.log10(0.125)
        rows.append(
            {
                "at": at,
                "event": name,
                "sfx_dbfs_250ms": round(sfx_db, 2),
                "pre_sfx_dbfs": round(pre_db, 2),
                "event_delta_db": round(sfx_db - pre_db, 2),
                "sfx_above_bed_db": round(sfx_db - bed_db, 2),
                "final_mix_dbfs": round(dbfs_window(final_audio, final_rate, at), 2),
            }
        )
    payload = {
        "exact_final_sha256": final_hash,
        "events": rows,
        "all_events_present": all(row["event_delta_db"] >= 3 or row["at"] <= 0.05 for row in rows),
        "all_events_above_bed": all(row["sfx_above_bed_db"] >= 3 for row in rows),
    }
    SFX_AUDIT.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def main() -> None:
    required = [FINAL, SOURCE, TIMELINE, ASSET_MANIFEST, TIMED_SFX, MUSIC_BED, WHISPER_PYTHON, TRANSCRIBE]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)
    CHECKS.mkdir(parents=True, exist_ok=True)
    for directory in (FRAMES, HOOK_FRAMES, MIDPOINT_FRAMES, BOUNDARY_FRAMES, SOURCE_SWEEP_FRAMES, CRITICAL_FRAMES):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)

    probe_text = cmd(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-count_frames", "-of", "json", FINAL])
    (CHECKS / "final-probe.json").write_text(probe_text)
    probe = json.loads(probe_text)
    video = next(item for item in probe["streams"] if item["codec_type"] == "video")
    audio = next(item for item in probe["streams"] if item["codec_type"] == "audio")
    final_duration = float(probe["format"]["duration"])
    final_hash = sha256(FINAL)

    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], text=True, capture_output=True, cwd=ROOT)
    black = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "blackdetect=d=0.20:pix_th=0.05", "-an", "-f", "null", "-"])
    freeze = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "freezedetect=n=-50dB:d=1.20", "-an", "-f", "null", "-"])
    silence = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-af", "silencedetect=n=-45dB:d=0.70", "-vn", "-f", "null", "-"])
    loud_log = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"])
    loud_matches = re.findall(r"\{\s*\"input_i\".*?\}", loud_log, re.DOTALL)
    if not loud_matches:
        raise RuntimeError("Unable to parse loudness")
    loud = json.loads(loud_matches[-1])
    for name, text in (
        ("decode.log", decode.stderr), ("blackdetect.log", black), ("freezedetect.log", freeze),
        ("silencedetect.log", silence), ("loudness.log", loud_log),
    ):
        (CHECKS / name).write_text(text)

    cmd(["ffmpeg", "-y", "-v", "error", "-t", "10", "-i", FINAL, "-vf", "fps=2,scale=216:384,tile=5x4:padding=4:margin=4", "-frames:v", "1", CHECKS / "hook-0-10-contact-sheet.jpg"])
    cmd(["ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vf", "fps=1/2,scale=162:288,tile=6x6:padding=4:margin=4", "-frames:v", "1", CHECKS / "full-contact-sheet.jpg"])
    cmd(["ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vf", "fps=1/2,scale=270:480", FRAMES / "frame-%03d.jpg"])
    cmd(["ffmpeg", "-y", "-v", "error", "-t", "6", "-i", FINAL, "-vf", "fps=10,scale=270:480", HOOK_FRAMES / "hook-%03d.jpg"])

    timeline_payload = json.loads(TIMELINE.read_text())
    timeline = timeline_payload["timeline"]
    beats = timeline_payload["beats"]
    for index, item in enumerate(timeline):
        midpoint = (float(item["final_start"]) + float(item["final_end"])) / 2
        extract_frame(midpoint, MIDPOINT_FRAMES / f"{index:02d}-{item['name']}.jpg")
    make_contact_sheet(str(MIDPOINT_FRAMES / "*.jpg"), CHECKS / "segment-midpoints.jpg", cols=4, rows=3)

    for index, boundary in enumerate(row["start"] for row in beats[1:]):
        for suffix, offset in (("pre", -0.08), ("post", 0.08)):
            extract_frame(max(0, float(boundary) + offset), BOUNDARY_FRAMES / f"{index:02d}-{suffix}.jpg", width=162, height=288)
    make_contact_sheet(str(BOUNDARY_FRAMES / "*.jpg"), CHECKS / "beat-boundary-pairs.jpg", cols=12, rows=7, width=108, height=192)

    source_items = [item for item in timeline if float(item.get("source_duration", 0)) > 0]
    sweep_index = 0
    for item in source_items:
        start = float(item["final_start"])
        end = float(item["final_end"])
        for label, at in (("start", start + 0.15), ("mid", (start + end) / 2), ("end", end - 0.15)):
            extract_frame(at, SOURCE_SWEEP_FRAMES / f"{sweep_index:02d}-{item['name']}-{label}.jpg")
            sweep_index += 1
    make_contact_sheet(str(SOURCE_SWEEP_FRAMES / "*.jpg"), CHECKS / "source-sweep.jpg", cols=3, rows=3)

    critical_times = (0.1, 1.6, 3.1, 6.1, 10.6, 16.6, 25.6, 31.6, 36.2, 38.2, 40.6, 43.6, 46.6, 49.6, 52.6, 58.6, 60.1, 64.3)
    for index, at in enumerate(critical_times):
        extract_frame(at, CRITICAL_FRAMES / f"{index:02d}-{at:05.1f}.jpg", width=540, height=960)
    make_contact_sheet(str(CRITICAL_FRAMES / "*.jpg"), CHECKS / "critical-frames.jpg", cols=6, rows=3, width=180, height=320)

    hook_paths = sorted(HOOK_FRAMES.glob("*.jpg"))
    hook_arrays = [np.asarray(Image.open(path).convert("L"), dtype=np.float32) for path in hook_paths]
    hook_deltas = [float(np.abs(left - right).mean()) for left, right in zip(hook_arrays, hook_arrays[1:])]
    median_hook_delta = float(np.median(hook_deltas)) if hook_deltas else 0
    sustained_frozen_hook = any(max(hook_deltas[index:index + 5], default=0) <= 1 for index in range(max(0, len(hook_deltas) - 4)))
    hook_skin = {str(index): skin_ratio(path) for index, path in enumerate(hook_paths[::10])}

    footer_ratios = []
    stddevs = []
    for path in sorted(FRAMES.glob("*.jpg")):
        image = Image.open(path).convert("L")
        width, height = image.size
        bottom = image.crop((0, int(height * 0.86), width, height))
        middle = image.crop((0, int(height * 0.35), width, int(height * 0.70)))
        footer_ratios.append(ImageStat.Stat(bottom).mean[0] / max(1, ImageStat.Stat(middle).mean[0]))
        stddevs.append(ImageStat.Stat(image).stddev[0])

    keyframes_data = json.loads(cmd([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=key_frame,best_effort_timestamp_time", "-of", "json", FINAL,
    ]))
    keyframes = [
        float(row["best_effort_timestamp_time"])
        for row in keyframes_data.get("frames", [])
        if int(row.get("key_frame", 0)) == 1 and "best_effort_timestamp_time" in row
    ]
    boundaries = [float(row["start"]) for row in beats]
    keyframe_errors = [min(abs(at - key) for key in keyframes) for at in boundaries]

    cmd([WHISPER_PYTHON, TRANSCRIBE, FINAL, ASR_JSON, "--model", ASR_MODEL, "--language", "en"])
    asr = json.loads(ASR_JSON.read_text())
    asr_text = normalize_text(str(asr.get("text", "")))
    required_patterns = {
        "export_crude": r"export.*crude|crude.*export",
        "import_products": r"import.*products|import.*fuel",
        "twenty_billion": r"twenty billion|20 billion",
        "refinery": r"\brefinery\b",
        "backward_integration": r"backward integration",
        "supplier": r"\bsupplier\b",
        "timing": r"\btiming\b",
        "quality": r"\bquality\b",
        "cost": r"\bcost\b",
        "six_fifty": r"six hundred fifty thousand|650 thousand|650 000",
        "dependency_upstream": r"dependency.*upstream|upstream.*dependency",
        "cta_like": r"\blike\b",
        "cta_subscribe": r"\bsubscribe\b",
        "cta_comment": r"\bcomment\b",
        "forty_six": r"forty six percent|46 percent|46%",
        "allocated_crude": r"allocated crude",
        "cargoes": r"thirteen to fifteen cargoe?s|13 to 15 cargoe?s",
        "imported_rest": r"imported the rest",
        "vertical_integration": r"vertical integration",
        "bottleneck": r"\bbottleneck\b",
        "bigger_bet": r"bet bigger|bigger.*bet",
        "build_supplier": r"build your supplier",
    }
    token_checks = {name: re.search(pattern, asr_text) is not None for name, pattern in required_patterns.items()}
    hook_asr = word_window(asr, 0, 12.0)
    cta_asr = word_window(asr, 37.5, 42.0)
    tail_asr = word_window(asr, 54.0, 64.5)

    sfx = audit_sfx(final_hash)
    source_seconds = sum(float(item["source_duration"]) for item in source_items)
    caption_rows = [row for rows in renderer.CAPTIONS.values() for row in rows]
    stock_manifest = json.loads(ASSET_MANIFEST.read_text())
    referenced_stock = {str(item["visual"]) for item in timeline if item.get("visual")}
    approved_stock = {str(item["path"]) for item in stock_manifest["approved"]}
    rejected_ids = {str(item["id"]) for item in stock_manifest["rejected"]}
    final_input_text = " ".join(str(item) for item in timeline)

    checks = {
        "duration_50_75": 50 <= final_duration <= 75,
        "duration_exact_64_5": abs(final_duration - 64.5) <= 0.08,
        "h264_1080x1920_yuv420p": video.get("codec_name") == "h264" and video.get("width") == 1080 and video.get("height") == 1920 and video.get("pix_fmt") == "yuv420p",
        "fps_30": video.get("r_frame_rate") == "30/1" and video.get("avg_frame_rate") == "30/1",
        "aac_48k_stereo": audio.get("codec_name") == "aac" and audio.get("sample_rate") == "48000" and audio.get("channels") == 2,
        "frame_count_1935": int(video.get("nb_read_frames", 0)) == 1935,
        "full_decode": decode.returncode == 0 and not decode.stderr.strip(),
        "beat_count_43": len(beats) == 43,
        "beat_contiguous": all(abs(float(left["end"]) - float(right["start"])) < 0.002 for left, right in zip(beats, beats[1:])),
        "max_visual_state_1_5": all(float(row["end"]) - float(row["start"]) <= 1.5001 for row in beats),
        "keyframe_each_beat": max(keyframe_errors) <= 1 / 30 + 0.001,
        "caption_by_0_2": renderer.CAPTIONS["export_import_quote"][0][0] <= 0.2,
        "caption_bursts_2_5_words": all(2 <= len(text.split()) <= 5 for _, _, text, _ in caption_rows),
        "cta_covers_38_42": next(float(item["final_start"]) for item in timeline if item["name"] == "triple_cta") <= 38 and next(float(item["final_end"]) for item in timeline if item["name"] == "triple_cta") >= 42.0,
        "source_each_under_15": all(float(item["source_duration"]) < 15 for item in source_items),
        "source_final_under_half": source_seconds < final_duration * 0.5,
        "source_master_under_half": source_seconds < duration(SOURCE) * 0.5,
        "exact_stock_manifest": referenced_stock == approved_stock,
        "rejected_stock_absent": all(asset_id not in final_input_text for asset_id in rejected_ids),
        "black_events_zero": black.count("black_start:") == 0,
        "freeze_events_zero": freeze.count("freeze_start:") == 0,
        "silence_events_zero": silence.count("silence_start:") == 0,
        "no_persistent_black_footer": all(value >= 0.08 for value in footer_ratios),
        "sampled_frames_content_rich": min(stddevs) >= 20,
        "hook_real_motion": median_hook_delta > 1 and not sustained_frozen_hook,
        "hook_face_gate": max(hook_skin.values()) >= 0.08,
        "loudness_window": -18 <= float(loud["input_i"]) <= -14,
        "true_peak_ceiling": float(loud["input_tp"]) <= -1,
        "final_asr_all_required": all(token_checks.values()),
        "targeted_hook_asr": "export" in hook_asr and "import" in hook_asr and ("twenty billion" in hook_asr or "20 billion" in hook_asr),
        "targeted_cta_asr": all(token in cta_asr for token in ("like", "subscribe", "comment")),
        "targeted_tail_asr": "vertical integration" in tail_asr and "bottleneck" in tail_asr and "build your supplier" in tail_asr,
        "sfx_events_present": bool(sfx["all_events_present"]),
        "sfx_events_above_bed": bool(sfx["all_events_above_bed"]),
    }
    summary = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "sha256": final_hash,
        "duration": final_duration,
        "frame_count": video.get("nb_read_frames"),
        "video": {key: video.get(key) for key in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate", "avg_frame_rate")},
        "audio": {
            "codec": audio.get("codec_name"), "sample_rate": audio.get("sample_rate"), "channels": audio.get("channels"),
            "integrated_lufs": float(loud["input_i"]), "true_peak_dbtp": float(loud["input_tp"]), "lra": float(loud["input_lra"]),
        },
        "source_use_seconds": source_seconds,
        "source_master_seconds": duration(SOURCE),
        "hook_motion": {"median_frame_delta": median_hook_delta, "sustained_frozen_interval": sustained_frozen_hook, "skin_ratios": hook_skin},
        "detectors": {"black_events": black.count("black_start:"), "freeze_events": freeze.count("freeze_start:"), "silence_events": silence.count("silence_start:")},
        "keyframes": {"count": len(keyframes), "maximum_boundary_error": max(keyframe_errors)},
        "asr": {"model": ASR_MODEL, "text": str(asr.get("text", "")).strip(), "required_tokens": token_checks, "hook_window": hook_asr, "cta_window": cta_asr, "tail_window": tail_asr},
        "evidence": {
            "hook_contact_sheet": str((CHECKS / "hook-0-10-contact-sheet.jpg").relative_to(ROOT)),
            "full_contact_sheet": str((CHECKS / "full-contact-sheet.jpg").relative_to(ROOT)),
            "segment_midpoints": str((CHECKS / "segment-midpoints.jpg").relative_to(ROOT)),
            "beat_boundaries": str((CHECKS / "beat-boundary-pairs.jpg").relative_to(ROOT)),
            "source_sweep": str((CHECKS / "source-sweep.jpg").relative_to(ROOT)),
            "critical_frames": str((CHECKS / "critical-frames.jpg").relative_to(ROOT)),
            "final_asr": str(ASR_JSON.relative_to(ROOT)),
            "sfx_event_audit": str(SFX_AUDIT.relative_to(ROOT)),
        },
        "checks": checks,
        "automated_pass": all(checks.values()),
        "manual_visual_qc": "pending exact-final image review",
    }
    (CHECKS / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if not summary["automated_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
