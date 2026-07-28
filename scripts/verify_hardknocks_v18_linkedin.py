#!/usr/bin/env python3
"""Verify the exact HardKnocks V18 LinkedIn artifact and emit evidence JSON."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "output" / "projects" / "hardknocks" / "final" / "2026-07-28-hardknocks_v18_linkedin_contrarian_test.mp4"
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v18_linkedin_work"
CHECKS = WORK / "checks"
HOOK_FRAMES = CHECKS / "hook_frames"
KEY_FRAMES = CHECKS / "key_frames"
FULL_FRAMES = CHECKS / "full_frames"
ASR_DIR = CHECKS / "asr"

WIDTH, HEIGHT, FPS = 1080, 1920, 30
for directory in (CHECKS, HOOK_FRAMES, KEY_FRAMES, FULL_FRAMES, ASR_DIR):
    directory.mkdir(parents=True, exist_ok=True)

MONTAGE_SCRIPT = (Path(__file__).parent / "verify_montage.py").read_text(encoding="utf-8")


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(a) for a in args], cwd=ROOT, text=True,
        capture_output=True, check=check,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path = FINAL) -> dict:
    return json.loads(run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path),
    ]).stdout)


def extract_frame(t: float, target: Path) -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(FINAL),
        "-frames:v", "1", str(target),
    ])


def make_sheet(input_dir: Path, output: Path, cols: int, width: int) -> Path:
    runner = CHECKS / "montage_runner.py"
    runner.write_text(MONTAGE_SCRIPT, encoding="utf-8")
    result = run([
        "python3", str(runner), "--input-dir", str(input_dir), "--output", str(output),
        "--cols", str(cols), "--thumb-width", str(width),
    ], check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return output


def media_detectors() -> tuple[dict[str, bool], dict[str, str]]:
    full = run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"])
    black = run([
        "ffmpeg", "-i", str(FINAL), "-vf", "blackdetect=d=0.12:pix_th=0.20",
        "-an", "-f", "null", "-",
    ])
    freeze_silence = run([
        "ffmpeg", "-i", str(FINAL),
        "-vf", "freezedetect=n=0.003:d=1.0",
        "-af", "silencedetect=noise=-35dB:d=0.55",
        "-f", "null", "-",
    ])
    logs = {
        "full_decode": full.stderr or "",
        "black": black.stderr or "",
        "freeze_silence": freeze_silence.stderr or "",
    }
    for name, content in logs.items():
        (CHECKS / f"{name}.log").write_text(content, encoding="utf-8")
    checks = {
        "full_decode_clean": full.returncode == 0,
        "black_events_zero": "black_start" not in logs["black"],
        "freeze_events_zero": "freeze_start" not in logs["freeze_silence"],
        "silence_events_zero": "silence_start" not in logs["freeze_silence"],
    }
    return checks, logs


def measure_loudness() -> dict[str, float | str | None]:
    result = run([
        "ffmpeg", "-i", str(FINAL),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=10:print_format=json",
        "-f", "null", "-",
    ], check=False)
    (CHECKS / "loudnorm.log").write_text(result.stderr or "", encoding="utf-8")
    matches = re.findall(r"\{[\s\S]*?\}", result.stderr or "")
    if not matches:
        return {"error": "loudnorm JSON not found"}
    raw = json.loads(matches[-1])
    return {
        "input_i": float(raw["input_i"]),
        "input_tp": float(raw["input_tp"]),
        "input_lra": float(raw["input_lra"]),
        "input_thresh": float(raw["input_thresh"]),
    }


def extract_review_frames(duration: float) -> dict[str, str]:
    hook_targets = (0.00, 0.20, 0.60, 1.00, 1.50, 2.00, 2.50, 3.00, 3.88, 4.40, 5.00)
    key_targets = (
        0.00, 3.88, 6.86, 10.32, 14.66, 16.10, 18.40, 20.90, 23.40,
        28.80, 35.60, 39.53, 41.20, 43.53, 47.20, 51.97, 54.00, 56.53,
        59.00, 61.47, 64.50, max(0.0, duration - 0.30),
    )
    for index, t in enumerate(hook_targets):
        extract_frame(t, HOOK_FRAMES / f"hook_{index:02d}_t{t:05.2f}.png")
    for index, t in enumerate(key_targets):
        extract_frame(t, KEY_FRAMES / f"key_{index:02d}_t{t:05.2f}.png")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(FINAL),
        "-vf", "fps=1", "-vsync", "vfr", str(FULL_FRAMES / "f_%03d.jpg"),
    ])
    return {
        "hook_sheet": str(make_sheet(HOOK_FRAMES, CHECKS / "contact_hook.jpg", 4, 270)),
        "key_sheet": str(make_sheet(KEY_FRAMES, CHECKS / "contact_key.jpg", 6, 216)),
        "full_sheet": str(make_sheet(FULL_FRAMES, CHECKS / "contact_full.jpg", 6, 180)),
    }


def footer_scan() -> dict[str, float | bool]:
    ratios: list[float] = []
    bottoms: list[float] = []
    for path in sorted(FULL_FRAMES.glob("f_*.jpg")):
        image = Image.open(path).convert("RGB")
        upper = image.crop((0, 0, image.width, 1650))
        bottom = image.crop((0, 1650, image.width, image.height))
        upper_mean = sum(ImageStat.Stat(upper).mean) / 3
        bottom_mean = sum(ImageStat.Stat(bottom).mean) / 3
        ratios.append(bottom_mean / max(upper_mean, 1.0))
        bottoms.append(bottom_mean)
    return {
        "minimum_bottom_mean": min(bottoms),
        "minimum_bottom_to_upper_ratio": min(ratios),
        "permanent_black_footer_absent": not all(value < 8.0 for value in bottoms),
    }


def extract_wav(name: str, start: float, duration: float | None) -> Path:
    output = ASR_DIR / f"{name}.wav"
    args = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(FINAL)]
    if duration is not None:
        args.extend(["-t", f"{duration:.3f}"])
    args.extend(["-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(output)])
    run(args)
    return output


def transcribe_windows(duration: float) -> tuple[dict[str, dict], dict[str, bool]]:
    import mlx_whisper

    windows = {
        "hook_0_10": (0.0, 10.0),
        "bridge_cta_34_45": (34.0, 11.5),
        "payoff_50_end": (50.0, duration - 50.0),
        "full": (0.0, None),
    }
    results: dict[str, dict] = {}
    for name, (start, length) in windows.items():
        wav = extract_wav(name, start, length)
        result = mlx_whisper.transcribe(
            str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
            word_timestamps=True, language="en", verbose=False,
        )
        (ASR_DIR / f"{name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        raw_text = result.get("text", "")
        text = raw_text if isinstance(raw_text, str) else str(raw_text)
        results[name] = {"text": text.strip(), "json": str(ASR_DIR / f"{name}.json")}

    hook = results["hook_0_10"]["text"].lower()
    bridge = results["bridge_cta_34_45"]["text"].lower()
    payoff = results["payoff_50_end"]["text"].lower()
    checks = {
        "hook_two_thirds": "two-thirds" in hook or "two thirds" in hook,
        "hook_linkedin": "linkedin" in hook,
        "hook_failure_test": "wrong" in hook and "fail" in hook,
        "bridge_not_blind": "not blind confidence" in bridge,
        "bridge_survivable_bet": "survivable bet" in bridge,
        "cta_like_subscribe_comment": all(word in bridge for word in ("like", "subscribe", "comment")),
        "payoff_26_billion": "26 billion" in payoff or "$26 billion" in payoff,
        "payoff_microsoft": "microsoft" in payoff,
        "payoff_worth_it": "worth it" in payoff,
    }
    return results, checks


def main() -> int:
    if not FINAL.exists():
        raise FileNotFoundError(FINAL)
    data = probe()
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    spec_checks = {
        "width": video.get("width") == WIDTH,
        "height": video.get("height") == HEIGHT,
        "codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "frame_rate": video.get("r_frame_rate") == "30/1",
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
        "duration": 50.0 <= duration <= 75.0,
    }
    detector_checks, _ = media_detectors()
    loudness = measure_loudness()
    sheets = extract_review_frames(duration)
    footer = footer_scan()
    asr, asr_checks = transcribe_windows(duration)
    loud_i_value = loudness.get("input_i")
    loud_tp_value = loudness.get("input_tp")
    loud_i = float(loud_i_value) if isinstance(loud_i_value, (float, int, str)) else -99.0
    loud_tp = float(loud_tp_value) if isinstance(loud_tp_value, (float, int, str)) else 99.0
    loudness_checks = {
        "integrated_loudness": -18.0 <= loud_i <= -14.0,
        "true_peak": loud_tp <= -1.0,
    }
    report = {
        "final": str(FINAL),
        "duration": duration,
        "size_bytes": int(data["format"]["size"]),
        "sha256": sha256(FINAL),
        "spec_checks": spec_checks,
        "detector_checks": detector_checks,
        "loudness": loudness,
        "loudness_checks": loudness_checks,
        "footer_scan": footer,
        "asr_checks": asr_checks,
        "asr": asr,
        "review_artifacts": sheets,
    }
    path = CHECKS / "validation.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    all_checks = (
        all(spec_checks.values()) and all(detector_checks.values()) and
        all(loudness_checks.values()) and bool(footer["permanent_black_footer_absent"]) and
        all(asr_checks.values())
    )
    return 0 if all_checks else 1


if __name__ == "__main__":
    sys.exit(main())
