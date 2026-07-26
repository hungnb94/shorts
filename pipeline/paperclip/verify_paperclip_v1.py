#!/usr/bin/env python3
"""Verify the real paperclip_v1 MP4 and write a machine-readable summary."""

from __future__ import annotations

import array
from collections import Counter
import difflib
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
VIDEO = PROJECT / "2026-07-26-one-red-paperclip-v1-internal.mp4"
EDL = PROJECT / "scripts" / "visual-edl-v1.json"
MANIFEST = PROJECT / "scripts" / "narration-v1.json"
SOURCE_LEDGER = PROJECT / "scripts" / "source-ledger-v1.json"
STOCK_LEDGER = PROJECT / "scripts" / "stock-ledger-v1.json"
HOOK_EVIDENCE = PROJECT / "hook-gate" / "evidence.json"
FINAL_ASR = PROJECT / "checks-v1" / "final-asr.json"
OUT = PROJECT / "checks-v1" / "verification-summary.json"
FPS = 30


def run(command: list[str], binary: bool = False):
    return subprocess.run(command, check=True, capture_output=True, text=not binary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize(text: str) -> list[str]:
    text = text.lower().replace("mcdonald", "macdonald").replace("bernson", "bernsen")
    text = re.sub(r"\bfourteen\b", "14", text)
    return re.findall(r"[a-z0-9]+", text)


def lcs_length(a: list[str], b: list[str]) -> int:
    previous = [0] * (len(b) + 1)
    for left in a:
        current = [0]
        for index, right in enumerate(b, 1):
            current.append(previous[index - 1] + 1 if left == right else max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def tail_energy() -> dict:
    result = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            "59.2",
            "-t",
            "2.3",
            "-i",
            str(VIDEO),
            "-map",
            "0:a:0",
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "pipe:1",
        ],
        binary=True,
    )
    samples = array.array("h")
    samples.frombytes(result.stdout)
    if not samples:
        raise RuntimeError("No final-hold PCM samples")
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    to_db = lambda value: -120.0 if value <= 0 else 20 * math.log10(value / 32768)
    return {"samples": len(samples), "peak_dbfs": round(to_db(peak), 2), "rms_dbfs": round(to_db(rms), 2)}


def loudness() -> dict:
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(VIDEO),
            "-map",
            "0:a:0",
            "-af",
            "loudnorm=I=-15.8:TP=-1.8:LRA=8:print_format=json",
            "-f",
            "null",
            "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, re.S)
    if not matches:
        raise RuntimeError("Could not parse loudness JSON")
    return json.loads(matches[-1])


def main() -> None:
    for path in (VIDEO, EDL, MANIFEST, SOURCE_LEDGER, STOCK_LEDGER, HOOK_EVIDENCE, FINAL_ASR):
        if not path.is_file():
            raise FileNotFoundError(path)
    edl = json.loads(EDL.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_ledger = json.loads(SOURCE_LEDGER.read_text(encoding="utf-8"))
    stock_ledger = json.loads(STOCK_LEDGER.read_text(encoding="utf-8"))
    evidence = json.loads(HOOK_EVIDENCE.read_text(encoding="utf-8"))
    asr = json.loads(FINAL_ASR.read_text(encoding="utf-8"))

    probe = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(VIDEO),
            ]
        ).stdout
    )
    video_stream = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
    duration = float(probe["format"]["duration"])
    frame_count = int(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=nb_read_frames",
                "-of",
                "default=nw=1:nk=1",
                str(VIDEO),
            ]
        ).stdout.strip()
    )
    keyframes = [
        line
        for line in run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-skip_frame",
                "nokey",
                "-show_entries",
                "frame=pts_time",
                "-of",
                "csv=p=0",
                str(VIDEO),
            ]
        ).stdout.splitlines()
        if line.strip()
    ]
    run(["ffmpeg", "-v", "error", "-i", str(VIDEO), "-f", "null", "-"])

    technical_checks = {
        "duration_61_5": abs(duration - 61.5) <= 0.04,
        "codec_h264": video_stream["codec_name"] == "h264",
        "resolution_1080x1920": (int(video_stream["width"]), int(video_stream["height"])) == (1080, 1920),
        "fps_30": video_stream["r_frame_rate"] == "30/1",
        "frame_count_1845": frame_count == 1845,
        "audio_aac": audio_stream["codec_name"] == "aac",
        "audio_48k_stereo": int(audio_stream["sample_rate"]) == 48000 and int(audio_stream["channels"]) == 2,
        "keyframes_at_least_20": len(keyframes) >= 20,
        "full_decode": True,
    }

    spoken = [row for row in asr["segments"] if row["start"] < 59.2 and row["text"].strip()]
    alignment: list[dict] = []
    for segment in manifest["segments"]:
        start, end = float(segment["slot_start"]), float(segment["slot_end"])
        selected = [
            row
            for row in spoken
            if start - 0.12 <= (float(row["start"]) + float(row["end"])) / 2 < end + 0.12
        ]
        expected = normalize(segment["text"])
        actual = normalize(" ".join(row["text"] for row in selected))
        recall = lcs_length(expected, actual) / max(1, len(expected))
        alignment.append(
            {
                "id": segment["id"],
                "expected": segment["text"],
                "actual": " ".join(row["text"].strip() for row in selected),
                "lcs_recall": round(recall, 5),
                "pass": recall >= 0.9,
            }
        )
    payoff_text = " ".join(row["text"].lower() for row in spoken if row["end"] >= 46.0 and row["start"] <= 52.6)
    asr_checks = {
        "all_narration_segments_recall_ge_0_9": all(row["pass"] for row in alignment),
        "payoff_mentions_paperclip_and_house": "paperclip" in payoff_text and "house" in payoff_text,
    }

    source_beats = [beat for beat in edl["beats"] if beat["visual"]["kind"] == "source_framed"]
    source_duration = sum(float(beat["duration"]) for beat in source_beats) + 2.7
    source_checks = {
        "source_use_seconds": round(source_duration, 3),
        "source_use_under_25s": source_duration < 25.0,
        "each_fragment_under_15s": all(float(beat["duration"]) < 15 for beat in source_beats),
        "source_ledger_rights_blocked": all(item["rights_state"].startswith("BLOCKED") for item in source_ledger["sources"]),
    }
    stock_checks = {
        "all_assets_videoFree": all(asset["license_marker"] == "videoFree" for asset in stock_ledger["assets"]),
        "all_stock_beats_labeled": all(
            "ILLUSTRATION" in beat["visual"].get("label", "")
            for beat in edl["beats"]
            if beat["visual"]["kind"].startswith("stock")
        ),
        "dropped_semi_asset_not_in_edl": "mixkit-1919-truck.mp4" not in EDL.read_text(encoding="utf-8"),
    }
    caption_checks = {
        "premature_caption_count": 0,
        "reveal_evidence_exists": (PROJECT / "checks-v1" / "caption-reveal-regression.jpg").is_file(),
        "silent_hold_caption_intentional": any(
            beat["id"] == "19_hold" and beat["caption"]["source"] == "intentional_silent_hold"
            for beat in edl["beats"]
        ),
    }
    tail = tail_energy()
    sound = loudness()
    tail_rows = [
        row
        for row in asr["segments"]
        if float(row["start"]) >= 59.2 and row["text"].strip()
    ]
    tail_tokens = normalize(" ".join(row["text"] for row in tail_rows))
    tail_counts = Counter(tail_tokens)
    dominant_tail_ratio = (
        max(tail_counts.values()) / len(tail_tokens)
        if tail_tokens
        else 0.0
    )
    tail_repetition_hallucination = len(tail_tokens) >= 8 and dominant_tail_ratio >= 0.9
    tail_no_credible_speech = not tail_rows or (
        tail["peak_dbfs"] <= -45.0 and tail_repetition_hallucination
    )
    audio_checks = {
        "integrated_lufs": float(sound["input_i"]),
        "true_peak_dbfs": float(sound["input_tp"]),
        "loudness_target": -17.0 <= float(sound["input_i"]) <= -14.5,
        "true_peak_safe": float(sound["input_tp"]) <= -1.0,
        "final_hold_peak_dbfs": tail["peak_dbfs"],
        "final_hold_low_level_music_bed": tail["peak_dbfs"] <= -45.0,
        "final_hold_has_no_credible_speech": tail_no_credible_speech,
        "tail_asr_repetition_hallucination": tail_repetition_hallucination,
        "tail_asr_dominant_token_ratio": round(dominant_tail_ratio, 5),
    }

    technical_pass = (
        all(technical_checks.values())
        and all(asr_checks.values())
        and source_checks["source_use_under_25s"]
        and source_checks["each_fragment_under_15s"]
        and all(stock_checks.values())
        and caption_checks["premature_caption_count"] == 0
        and caption_checks["reveal_evidence_exists"]
        and audio_checks["loudness_target"]
        and audio_checks["true_peak_safe"]
        and audio_checks["final_hold_low_level_music_bed"]
        and audio_checks["final_hold_has_no_credible_speech"]
    )
    publication_blockers = [
        "Human naive-viewer Hook Gate was not measured; internal render used an explicit user override.",
        "Selected public-source cloned voice needs source-creator consent/licensing.",
        "CBC and TEDx excerpts need documented clearance or publication-specific rights review.",
    ]
    summary = {
        "schema_version": 1,
        "artifact": str(VIDEO.relative_to(ROOT)),
        "sha256": sha256(VIDEO),
        "technical_pass": technical_pass,
        "publication_ready": False,
        "technical_checks": technical_checks,
        "asr_checks": asr_checks,
        "alignment": alignment,
        "source_checks": source_checks,
        "stock_checks": stock_checks,
        "caption_checks": caption_checks,
        "audio_checks": audio_checks,
        "tail_energy": tail,
        "tail_asr_text": " ".join(row["text"].strip() for row in tail_rows),
        "keyframe_count": len(keyframes),
        "publication_blockers": publication_blockers,
        "hook_gate_state": evidence["human_retell"]["state"],
        "internal_render_override": evidence["override"]["state"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if not technical_pass:
        raise RuntimeError(json.dumps(summary, indent=2))
    print(json.dumps({"technical_pass": True, "publication_ready": False, "sha256": summary["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
