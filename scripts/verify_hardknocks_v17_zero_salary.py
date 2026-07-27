#!/usr/bin/env python3
"""Verify the HardKnocks V17 $0 Salary Bet artifact and emit evidence JSON."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "output" / "projects" / "hardknocks" / "final" / "2026-07-27-hardknocks_v17_zero_salary_bet_r2_active_speaker.mp4"
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v17_zero_salary_work"
CHECKS = WORK / "checks_r2_active_speaker"
FRAMES = CHECKS / "frames"
ASR_DIR = CHECKS / "asr"

WIDTH, HEIGHT, FPS = 1080, 1920, 30

CHECKS.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)
ASR_DIR.mkdir(parents=True, exist_ok=True)

MONTAGE_SCRIPT = (Path(__file__).parent / "verify_montage.py").read_text(encoding="utf-8")


def run(args: list[str], *, check: bool = True, input_data: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(a) for a in args], cwd=ROOT, text=True,
                            capture_output=True, check=check, input=input_data)
    return result


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write(name: str, content: str) -> Path:
    out = CHECKS / name
    out.write_text(content, encoding="utf-8")
    return out


def probe() -> dict:
    result = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
        str(FINAL),
    ])
    return json.loads(result.stdout)


def full_decode() -> str:
    out = CHECKS / "full_decode.log"
    log_dir = CHECKS / "full_decode_stream"
    if log_dir.exists():
        shutil.rmtree(log_dir)
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(FINAL),
        "-f", "null", "-", "-progress", str(out.with_suffix(".progress")),
    ])
    log = out.read_text(encoding="utf-8") if out.exists() else ""
    write("full_decode.log", log)
    return log


def blackdetect() -> str:
    out = CHECKS / "black.log"
    result = run([
        "ffmpeg", "-i", str(FINAL), "-vf",
        "blackdetect=d=0.12:pix_th=0.20",
        "-an", "-f", "null", "-",
    ])
    out.write_text(result.stderr or "", encoding="utf-8")
    return out.read_text(encoding="utf-8")


def freeze_and_silence() -> tuple[str, str, str]:
    detector_log = CHECKS / "detectors.log"
    ff = subprocess.run([
        "ffmpeg", "-i", str(FINAL),
        "-vf", "freezedetect=n=0.003:d=1.0",
        "-af", "silencedetect=noise=-35dB:d=0.50,ametadata=mode=print:file=-",
        "-f", "null", "-",
    ], capture_output=True, text=True, check=True)
    detector_log.write_text(ff.stderr, encoding="utf-8")
    freeze_log = CHECKS / "freeze.log"
    sil_log = CHECKS / "silence.log"
    fz = run(["grep", "freeze_start", str(detector_log)], check=False).stdout
    sl = run(["grep", "silence_start", str(detector_log)], check=False).stdout
    freeze_log.write_text(fz, encoding="utf-8")
    sil_log.write_text(sl, encoding="utf-8")
    return fz, sl, detector_log.read_text(encoding="utf-8")


def loudnorm() -> str:
    out = CHECKS / "loudnorm.log"
    ff = subprocess.run([
        "ffmpeg", "-i", str(FINAL),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=10:print_format=summary",
        "-f", "null", "-",
    ], capture_output=True, text=True, check=False)
    out.write_text(ff.stderr, encoding="utf-8")
    return out.read_text(encoding="utf-8")


def extract_hook_frames() -> list[Path]:
    targets = [0.0, 0.2, 0.6, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    paths: list[Path] = []
    for t in targets:
        path = FRAMES / f"hook_t_{t:04.2f}.png"
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}",
            "-i", str(FINAL), "-frames:v", "1", str(path),
        ])
        paths.append(path)
    return paths


def contact_sheet(frame_paths: list[Path]) -> Path:
    out = FRAMES.parent / "contact_360x640.jpg"
    montage_path = CHECKS / "montage_runner.py"
    montage_path.write_text(MONTAGE_SCRIPT, encoding="utf-8")
    run(["python3", str(montage_path), "--input-dir", str(FRAMES), "--output", str(out),
         "--cols", "5", "--thumb-width", "360"], check=False)
    return out


def full_contact_sheet() -> Path:
    tmp = CHECKS / "full_frames"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    duration_ff = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
        "default=nw=1:nk=1", str(FINAL),
    ], capture_output=True, text=True, check=True)
    total = float(duration_ff.stdout.strip())
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(FINAL),
        "-vf", "fps=1", "-vsync", "vfr", str(tmp / "f_%03d.jpg"),
    ])
    out = CHECKS / "contact_full.jpg"
    montage_path = CHECKS / "montage_runner.py"
    montage_path.write_text(MONTAGE_SCRIPT, encoding="utf-8")
    run(["python3", str(montage_path), "--input-dir", str(tmp), "--output", str(out),
         "--cols", "6", "--thumb-width", "216"], check=False)
    return out


def extract_audio_mono() -> Path:
    wav = ASR_DIR / "final_mono_16k.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(FINAL),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav),
    ])
    return wav


def run_mlx_whisper(wav: Path) -> Path:
    try:
        import mlx_whisper
        result = mlx_whisper.transcribe(
            str(wav),
            path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
            word_timestamps=True,
        )
        out = ASR_DIR / "final_asr.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return out
    except Exception as e:
        err = ASR_DIR / "final_asr_error.txt"
        err.write_text(str(e), encoding="utf-8")
        return err


def main() -> int:
    print("Running full media QC for V17 Zero Salary Bet...")

    # Spec validation
    data = probe()
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    audio = next(s for s in data["streams"] if s["codec_type"] == "audio")
    duration = float(data["format"]["duration"])

    checks = {
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
    print(f"Spec checks: {checks}")

    # Full decode
    print("Full decode...")
    full_decode()

    # Black detect
    print("Black detect...")
    black_log = blackdetect()

    # Freeze/silence
    print("Freeze/silence detect...")
    freeze_log, silence_log, _ = freeze_and_silence()
    detector_checks = {
        "black_events_zero": "black_start" not in black_log,
        "freeze_events_zero": not freeze_log.strip(),
        "silence_events_zero": not silence_log.strip(),
    }
    print(f"Detector checks: {detector_checks}")

    # Loudnorm
    print("Loudness measurement...")
    loudnorm()

    # Hook frames
    print("Extracting hook frames...")
    hook_frames = extract_hook_frames()

    # Contact sheets
    print("Generating contact sheets...")
    mobile_sheet = contact_sheet(hook_frames)
    full_sheet = full_contact_sheet()

    # ASR
    print("Running mlx_whisper ASR...")
    wav = extract_audio_mono()
    asr_path = run_mlx_whisper(wav)

    # SHA-256
    digest = sha256(FINAL)
    print(f"SHA-256: {digest}")

    report = {
        "final": str(FINAL),
        "duration": duration,
        "spec_checks": checks,
        "detector_checks": detector_checks,
        "sha256": digest,
        "hooksheet": str(mobile_sheet),
        "full_sheet": str(full_sheet),
        "asr_json": str(asr_path),
    }
    (CHECKS / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Validation written to", CHECKS / "validation.json")
    return 0 if all(checks.values()) and all(detector_checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())