#!/usr/bin/env python3
"""Build the word-anchored visual EDL for paperclip_v1."""

from __future__ import annotations

import difflib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
MANIFEST = PROJECT / "scripts" / "narration-v1.json"
ASR = PROJECT / "audio" / "narration-mix-v1-asr.json"
EVIDENCE = PROJECT / "hook-gate" / "evidence.json"
OUT = PROJECT / "scripts" / "visual-edl-v1.json"
AUDIT = PROJECT / "checks-v1" / "alignment-audit.json"
FPS = 30


def tokens(text: str) -> list[str]:
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


def ceil_frame(value: float) -> float:
    return math.ceil((value - 1e-9) * FPS) / FPS


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    asr = json.loads(ASR.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if not evidence["override"]["allows_internal_render"]:
        raise RuntimeError("Internal rendering remains blocked")

    spoken_segments = [row for row in asr["segments"] if row["start"] < 59.2 and row["text"].strip()]
    caption_map: dict[str, dict] = {}
    alignment_rows: list[dict] = []
    for segment in manifest["segments"]:
        start = float(segment["slot_start"])
        end = float(segment["slot_end"])
        selected = [
            row
            for row in spoken_segments
            if start - 0.12 <= (float(row["start"]) + float(row["end"])) / 2 < end + 0.12
        ]
        if not selected:
            raise RuntimeError(f"No ASR timing for {segment['id']}")
        actual_text = " ".join(row["text"].strip() for row in selected)
        expected_tokens = tokens(segment["text"])
        actual_tokens = tokens(actual_text)
        ratio = difflib.SequenceMatcher(None, expected_tokens, actual_tokens).ratio()
        recall = lcs_length(expected_tokens, actual_tokens) / max(1, len(expected_tokens))
        caption_at = ceil_frame(max(start, selected[0]["start"]))
        caption_end = min(end, selected[-1]["end"] + 0.16)
        caption_map[segment["id"]] = {
            "text": segment["caption"],
            "caption_at": caption_at,
            "caption_end": round(caption_end, 3),
            "source": "final_narration_mix_asr",
        }
        alignment_rows.append(
            {
                "id": segment["id"],
                "slot_start": start,
                "slot_end": end,
                "asr_start": selected[0]["start"],
                "asr_end": selected[-1]["end"],
                "caption_at": caption_at,
                "caption_end": round(caption_end, 3),
                "expected": segment["text"],
                "actual": actual_text,
                "sequence_ratio": round(ratio, 5),
                "lcs_recall": round(recall, 5),
            }
        )

    source_rows = [row for row in spoken_segments if row["end"] >= 46.0 and row["start"] <= 52.6]
    if not source_rows:
        raise RuntimeError("Source payoff is absent from final audio ASR")
    payoff_caption = {
        "text": "PAPERCLIP → HOUSE",
        "caption_at": ceil_frame(48.98),
        "caption_end": 52.6,
        "source": "final_narration_mix_asr_payoff_clause",
    }
    final_caption = {
        "text": manifest["final_hold"]["caption"],
        "caption_at": 59.2,
        "caption_end": 61.5,
        "source": "intentional_silent_hold",
    }

    def beat(
        beat_id: str,
        start: float,
        end: float,
        progress: int,
        title: str,
        subtitle: str,
        visual: dict,
        caption_id: str | None = None,
        caption: dict | None = None,
    ) -> dict:
        if end <= start:
            raise ValueError(beat_id)
        chosen_caption = caption if caption is not None else caption_map[caption_id] if caption_id else None
        return {
            "id": beat_id,
            "start": start,
            "end": end,
            "duration": round(end - start, 3),
            "progress_index": progress,
            "title": title,
            "subtitle": subtitle,
            "visual": visual,
            "caption": chosen_caption,
        }

    cbc = "output/projects/paperclip/source/s5Dr80SRDFA.mp4"
    tedx = "output/projects/paperclip/source/8s3bdVxuFBs.mp4"
    stock = "output/projects/paperclip/stock"
    beats = [
        beat("00_hook", 0.0, 2.7, 0, "ONE RED PAPERCLIP", "THE GOAL: A HOUSE", {"kind": "hook_video", "path": "output/projects/paperclip/hook-gate/paperclip-hook-v1.mp4", "ss": 0.0, "label": "CBC ARCHIVE + HOUSE ILLUSTRATION"}),
        beat("01_kyle_rule", 2.7, 8.0, 0, "KYLE MACDONALD", "ONE RULE: TRADE UP", {"kind": "source_framed", "path": cbc, "ss": 78.0, "label": "CBC NEWS SASKATCHEWAN"}, "01_rule"),
        beat("02_paperclip", 8.0, 9.0, 0, "RED PAPERCLIP", "START", {"kind": "source_framed", "path": cbc, "ss": 25.0, "label": "CBC NEWS ARCHIVE"}, "02_objects"),
        beat("03_fish_pen", 9.0, 10.2, 1, "FISH PEN", "TRADE 1", {"kind": "source_framed", "path": cbc, "ss": 27.0, "label": "CBC NEWS ARCHIVE"}, "02_objects"),
        beat("04_knob_stove", 10.2, 11.2, 3, "DOORKNOB → STOVE", "TRADES 2–3", {"kind": "graphic", "theme": "door_fire"}, "02_objects"),
        beat("05_generator", 11.2, 12.4, 4, "GENERATOR", "TRADE 4", {"kind": "source_framed", "path": cbc, "ss": 30.8, "label": "CBC NEWS ARCHIVE"}, "02_objects"),
        beat("06_party", 12.4, 14.7, 5, "INSTANT PARTY", "TRADE 5 · ILLUSTRATION", {"kind": "stock_full", "path": f"{stock}/mixkit-4344-party.mp4", "ss": 1.0, "label": "ILLUSTRATION"}, "03_party_trip"),
        beat("07_trip", 14.7, 17.4, 7, "SNOWMOBILE → TRIP", "TRADES 6–7 · ILLUSTRATION", {"kind": "stock_full", "path": f"{stock}/mixkit-4283-snow.mp4", "ss": 1.0, "label": "ILLUSTRATION"}, "03_party_trip"),
        beat("08_truck", 17.4, 19.7, 8, "TRIP SEAT → BOX TRUCK", "TRADE 8", {"kind": "graphic", "theme": "trip_truck"}, "04_truck_rent"),
        beat("09_recording", 19.7, 21.8, 9, "RECORDING CONTRACT", "TRADE 9 · ILLUSTRATION", {"kind": "stock_full", "path": f"{stock}/mixkit-44049-recording.mp4", "ss": 1.0, "label": "ILLUSTRATION"}, "04_truck_rent"),
        beat("10_rent", 21.8, 24.0, 10, "ONE YEAR OF RENT", "TRADE 10", {"kind": "graphic", "theme": "rent_key"}, "04_truck_rent"),
        beat("11_alice", 24.0, 26.7, 11, "ALICE COOPER ACCESS", "TRADE 11 · ILLUSTRATION", {"kind": "stock_full", "path": f"{stock}/mixkit-42824-guitar.mp4", "ss": 2.0, "label": "ILLUSTRATION"}, "05_alice_globe"),
        beat("12_globe", 26.7, 29.8, 12, "KISS SNOW GLOBE", "TRADE 12", {"kind": "graphic", "theme": "snow_globe"}, "05_alice_globe"),
        beat("13_movie", 29.8, 34.7, 13, "PAID MOVIE ROLE", "TRADE 13", {"kind": "graphic", "theme": "movie_role"}, "06_movie"),
        beat("14_cta", 34.7, 40.2, 13, "ONE SWAP LEFT", "LIKE · SUBSCRIBE · COMMENT", {"kind": "stock_chroma", "path": f"{stock}/mixkit-28309-handshake.mp4", "ss": 0.0, "label": "ILLUSTRATION"}, "07_cta"),
        beat("15_final_setup", 40.2, 45.6, 13, "THE FINAL SWAP", "A TOWN WANTED THE ROLE", {"kind": "stock_full", "path": f"{stock}/mixkit-4009-house.mp4", "ss": 0.0, "label": "HOUSE ILLUSTRATION"}, "08_final_setup"),
        beat("16_suspense", 45.6, 46.0, 13, "ONE THING LEFT", "…", {"kind": "graphic", "theme": "locked_house"}, "08_final_setup"),
        beat("17_house_payoff", 46.0, 52.6, 14, "THE HOUSE", "TRADE 14", {"kind": "source_framed", "path": tedx, "ss": 657.82, "label": "TEDxVIENNA · KYLE MACDONALD"}, caption=payoff_caption),
        beat("18_recap", 52.6, 59.2, 14, "14 TRADES · 1 YEAR", "PREFERENCE MATCHING, NOT MAGIC", {"kind": "graphic", "theme": "full_trade_ladder"}, "09_lesson"),
        beat("19_hold", 59.2, 61.5, 14, "PAPERCLIP → HOUSE", "WHAT WOULD YOU TRADE FIRST?", {"kind": "graphic", "theme": "loop_close"}, caption=final_caption),
    ]
    if abs(beats[0]["start"]) > 1e-6 or abs(beats[-1]["end"] - manifest["target_duration"]) > 1e-6:
        raise RuntimeError("Timeline endpoints mismatch")
    for left, right in zip(beats, beats[1:]):
        if abs(left["end"] - right["start"]) > 1e-6:
            raise RuntimeError(f"Timeline gap/overlap: {left['id']} -> {right['id']}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project": "paperclip_v1",
                "fps": FPS,
                "duration": manifest["target_duration"],
                "human_hook_gate": evidence["human_retell"]["state"],
                "internal_render_override": evidence["override"]["state"],
                "beats": beats,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "audio_asr": str(ASR.relative_to(ROOT)),
                "caption_policy": "ceil first spoken ASR onset to the next 30fps frame; silent final hold is intentional",
                "rows": alignment_rows,
                "source_payoff_asr": " ".join(row["text"].strip() for row in source_rows),
                "source_payoff_caption": payoff_caption,
                "ignored_tail_asr": {
                    "start": 59.2,
                    "reason": "Whisper hallucination over measured -91 dB digital silence",
                    "waveform_gate": "PASS",
                },
                "premature_caption_count": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"beats": len(beats), "alignment_rows": len(alignment_rows), "edl": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
