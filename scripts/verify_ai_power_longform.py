#!/usr/bin/env python3
"""Evidence-first media QA for the exact AI power long-form MP4."""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output/projects/ai-power-bottleneck"
FINAL = PROJECT / "final/2026-07-28-ai_real_bottleneck_isnt_chips.mp4"
TIMELINE = PROJECT / "scripts/timeline.json"
SCRIPT = PROJECT / "scripts/script.json"
MANIFEST = PROJECT / "source/pexels-manifest.json"
CHECKS = PROJECT / "checks"
VALIDATION = CHECKS / "validation.json"
TRANSCRIPT = CHECKS / "final-asr.json"
ASR_META = CHECKS / "final-asr-meta.json"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def run(command: list[str | Path], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(part) for part in command], cwd=ROOT, text=True, capture_output=True, check=check)


def ffprobe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    return json.loads(result.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fps_value(value: str) -> float:
    numerator, denominator = value.split("/")
    return float(numerator) / float(denominator)


def detect(pattern: str, filter_graph: str) -> tuple[list[dict[str, float]], str]:
    result = run(["ffmpeg", "-hide_banner", "-nostats", "-i", FINAL, "-vf", filter_graph, "-an", "-f", "null", "-"], check=False)
    matches: list[dict[str, float]] = []
    for found in re.finditer(pattern, result.stderr):
        matches.append({key: float(value) for key, value in found.groupdict().items()})
    return matches, result.stderr


def loudness() -> dict[str, float]:
    result = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", FINAL,
        "-af", "loudnorm=I=-16:TP=-2.5:LRA=9:print_format=json", "-f", "null", "-",
    ], check=False)
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.S)
    if not blocks:
        raise RuntimeError("loudnorm JSON not found")
    payload = json.loads(blocks[-1])
    return {
        "integrated_lufs": float(payload["input_i"]),
        "true_peak_dbtp": float(payload["input_tp"]),
        "lra": float(payload["input_lra"]),
        "threshold": float(payload["input_thresh"]),
    }


def transcribe() -> dict[str, Any]:
    import mlx_whisper

    wav = CHECKS / "final-asr.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vn", "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le", wav,
    ])
    audio_sha256 = sha256(wav)
    if TRANSCRIPT.is_file() and ASR_META.is_file():
        meta = json.loads(ASR_META.read_text(encoding="utf-8"))
        if meta.get("audio_sha256") == audio_sha256:
            return json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
    result = mlx_whisper.transcribe(
        str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        word_timestamps=True, language="en", verbose=False,
    )
    TRANSCRIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ASR_META.write_text(json.dumps({"audio_sha256": audio_sha256}, indent=2) + "\n", encoding="utf-8")
    asr_text = str(result.get("text", "")).strip()
    (CHECKS / "final-asr.txt").write_text(asr_text + "\n", encoding="utf-8")
    return result


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def make_contact(name: str, interval: int, length: float, columns: int = 4, start: float = 0.0) -> Path:
    frames = CHECKS / f"{name}-frames"
    frames.mkdir(parents=True, exist_ok=True)
    for stale in frames.glob("*.jpg"):
        stale.unlink()
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", FINAL, "-t", f"{length:.3f}",
        "-vf", f"fps=1/{interval},scale=480:270", "-q:v", "2", frames / "%04d.jpg",
    ])
    paths = sorted(frames.glob("*.jpg"))
    if not paths:
        raise RuntimeError(f"no frames generated for {name}")
    label_height = 28
    tile_h = 270 + label_height
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * 480, rows * tile_h), "#090f19")
    face = ImageFont.truetype(FONT, 18)
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        x = (index % columns) * 480
        y = (index // columns) * tile_h
        sheet.paste(image, (x, y))
        timestamp = min(start + index * interval, start + length)
        draw.rectangle((x, y + 270, x + 480, y + tile_h), fill="#05080d")
        draw.text((x + 8, y + 274), f"t={timestamp:06.1f}s", font=face, fill="#f4f8fc")
    output = CHECKS / f"{name}.jpg"
    sheet.save(output, quality=90, optimize=True)
    return output


def main() -> None:
    CHECKS.mkdir(parents=True, exist_ok=True)
    checks: dict[str, dict[str, Any]] = {}

    def record(name: str, passed: bool, evidence: Any) -> None:
        checks[name] = {"pass": bool(passed), "evidence": evidence}
        print(("PASS" if passed else "FAIL"), name, evidence)

    if not FINAL.is_file():
        raise SystemExit(f"missing final: {FINAL}")
    info = ffprobe(FINAL)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    total = float(info["format"]["duration"])
    frame_rate = fps_value(video["avg_frame_rate"])

    record("duration_8_to_12_minutes", 480 <= total <= 720, total)
    record("resolution_16x9_full_hd", int(video["width"]) == 1920 and int(video["height"]) == 1080, [video["width"], video["height"]])
    record("frame_rate_30fps", abs(frame_rate - 30) < 0.01, frame_rate)
    record("h264_yuv420p", video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p", [video.get("codec_name"), video.get("pix_fmt")])
    record("aac_48khz_stereo", audio.get("codec_name") == "aac" and int(audio.get("sample_rate", 0)) == 48000 and int(audio.get("channels", 0)) == 2, [audio.get("codec_name"), audio.get("sample_rate"), audio.get("channels")])

    decode = run(["ffmpeg", "-v", "error", "-i", FINAL, "-f", "null", "-"], check=False)
    record("full_decode", decode.returncode == 0 and not decode.stderr.strip(), decode.stderr.strip() or "clean")

    black, _ = detect(
        r"black_start:(?P<start>[0-9.]+) black_end:(?P<end>[0-9.]+) black_duration:(?P<duration>[0-9.]+)",
        "blackdetect=d=0.65:pix_th=0.10",
    )
    record("no_black_frame_run_ge_0_65s", not black, black)
    freeze, _ = detect(
        r"freeze_start: (?P<start>[0-9.]+).*?freeze_duration: (?P<duration>[0-9.]+)",
        "freezedetect=n=-50dB:d=1.2",
    )
    record("no_freeze_ge_1_2s", not freeze, freeze)

    silence_result = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", FINAL,
        "-af", "silencedetect=noise=-45dB:d=1.2", "-vn", "-f", "null", "-",
    ], check=False)
    silences = [float(value) for value in re.findall(r"silence_duration: ([0-9.]+)", silence_result.stderr)]
    record("no_silence_ge_1_2s", not silences, silences)

    levels = loudness()
    record("integrated_loudness", -18.5 <= levels["integrated_lufs"] <= -14.5, levels)
    record("true_peak_safe", levels["true_peak_dbtp"] <= -1.5, levels["true_peak_dbtp"])

    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    record("timeline_matches_final", abs(float(timeline["duration"]) - total) <= 0.08, {"timeline": timeline["duration"], "final": total})
    record("timeline_scene_count", len(timeline["scenes"]) == 53, len(timeline["scenes"]))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stock_ok = len(manifest["assets"]) == 11 and all(
        item.get("classification") == "ILLUSTRATION"
        and int(item["actual_probe"]["width"]) >= 1920
        and int(item["actual_probe"]["height"]) >= 1080
        for item in manifest["assets"]
    )
    record("licensed_stock_manifest", stock_ok, len(manifest["assets"]))

    asr = transcribe()
    text = normalize(str(asr.get("text", "")))
    phrase_groups = {
        "hook": [["everyone"], ["ai race"], ["chips"]],
        "transformer_mechanism": [["power transformer"], ["servers"], ["wrong voltage"]],
        "demand_evidence": [
            ["four hundred billion", "400 billion"],
            ["four hundred eighty five", "485"],
            ["nine hundred fifty", "950"],
        ],
        "big_tech_deals": [["microsoft"], ["google"], ["meta"]],
        "payoff": [["where is the transformer"]],
        "cta": [["chips power or capital"], ["comments"], ["subscribe"]],
    }
    asr_checks = {
        name: all(any(alternative in text for alternative in alternatives) for alternatives in groups)
        for name, groups in phrase_groups.items()
    }
    record("asr_critical_content", all(asr_checks.values()), asr_checks)

    hook_contact = make_contact("contact-hook-2s", 2, min(42.0, total), columns=4)
    full_contact = make_contact("contact-full-10s", 10, total, columns=4)
    tail_start = max(0.0, total - 36.0)
    tail_contact = make_contact("contact-tail-2s", 2, total - tail_start, columns=4, start=tail_start)
    record(
        "contact_sheets_created",
        hook_contact.is_file() and full_contact.is_file() and tail_contact.is_file(),
        [str(hook_contact), str(full_contact), str(tail_contact)],
    )

    payload = {
        "status": "PASS" if all(item["pass"] for item in checks.values()) else "FAIL",
        "final": str(FINAL),
        "size_bytes": FINAL.stat().st_size,
        "sha256": sha256(FINAL),
        "duration": total,
        "checks": checks,
        "asr_text": str(asr.get("text", "")).strip(),
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    passed = sum(item["pass"] for item in checks.values())
    print(f"{passed}/{len(checks)} checks passed")
    print(VALIDATION)
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
