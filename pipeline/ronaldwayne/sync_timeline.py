#!/usr/bin/env python3
"""Build the Qwen-word-aligned 40-beat visual/caption manifest."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

FPS = 30
BEAT_DURATION = 1.5

BEAT_SPECS: list[dict[str, Any]] = [
    {"caption": "THE INTERNET SAYS", "anchor_phrase": "the internet says", "tokens": ["the", "internet", "says"], "visual": "bbc_video", "subcaption": "The popular version"},
    {"caption": "10% OF APPLE", "anchor_phrase": "ten percent of apple", "tokens": ["10", "percent", "of", "apple"], "visual": "apple_early", "subcaption": "Founding ownership"},
    {"caption": "FOR $800", "anchor_phrase": "eight hundred dollars", "tokens": ["800"], "visual": "contract_document", "subcaption": "The shorthand"},
    {"caption": "WAYNE CALLS THAT FALSE", "anchor_phrase": "wayne calls that false", "tokens": ["wayne", "calls", "that", "false"], "visual": "disputed_headline", "subcaption": "His later rebuttal"},
    {"caption": "WHAT ACTUALLY HAPPENED?", "anchor_phrase": "so what actually happened", "tokens": ["so", "what", "actually", "happened"], "visual": "bbc_video", "subcaption": "Follow the documents"},
    {"caption": "WAYNE DRAFTED IT", "anchor_phrase": "wayne drafted", "tokens": ["wayne", "drafted"], "visual": "wayne_document", "subcaption": "He helped write it"},
    {"caption": "PARTNERSHIP AGREEMENT", "anchor_phrase": "partnership agreement", "tokens": ["partnership", "agreement"], "visual": "contract_document", "subcaption": "Signed April 1, 1976"},
    {"caption": "NAME REMOVED / 12 DAYS LATER", "anchor_phrase": "removed his name twelve days later", "tokens": ["removed", "his", "name", "12", "days", "later"], "visual": "name_removed_timeline", "subcaption": "Twelve days later"},
    {"caption": "JOBS SENT $800", "anchor_phrase": "jobs later sent him eight hundred dollars", "tokens": ["jobs", "later", "sent", "him", "800"], "visual": "money_800", "subcaption": "A later payment"},
    {"caption": "APPLE WAS…", "anchor_phrase": "apple was", "tokens": ["apple", "was"], "visual": "liability_setup", "subcaption": "The structure mattered"},
    {"caption": "NOT A CORPORATION", "anchor_phrase": "not a corporation", "tokens": ["not", "a", "corporation"], "visual": "not_corporation", "subcaption": "Personal exposure"},
    {"caption": "PERSONAL LIABILITY", "anchor_phrase": "personally liable", "tokens": ["personally", "liable"], "visual": "partner_liability", "subcaption": "Each general partner"},
    {"caption": "JOBS + WOZ", "anchor_phrase": "jobs and wozniak", "tokens": ["jobs", "and", "wozniak"], "visual": "risk_split", "subcaption": "Different downside"},
    {"caption": "YOUNG AND BROKE", "anchor_phrase": "young and broke", "tokens": ["young", "and", "broke"], "visual": "young_broke_split", "subcaption": "Less to lose"},
    {"caption": "WAYNE WAS 41", "anchor_phrase": "wayne was forty one", "tokens": ["wayne", "was", "41"], "visual": "wayne_age", "subcaption": "Older, established"},
    {"caption": "HOUSE • CAR • MONEY", "anchor_phrase": "house a car and money", "tokens": ["house", "a", "car", "and", "money"], "visual": "grouped_assets", "subcaption": "Assets at risk"},
    {"caption": "CREDITORS COULD REACH", "anchor_phrase": "creditors could reach", "tokens": ["creditors", "could", "reach"], "visual": "creditor_exposure", "subcaption": "Potential exposure"},
    {"caption": "THE TWIST?", "anchor_phrase": "the twist", "tokens": ["the", "twist"], "visual": "twist_card", "subcaption": "Not disbelief"},
    {"caption": "WAYNE BELIEVED IN APPLE", "anchor_phrase": "wayne believed in apple", "tokens": ["wayne", "believed", "in", "apple"], "visual": "wayne_belief", "subcaption": "He still saw the upside"},
    {"caption": "IT WAS THE…", "anchor_phrase": "it was the", "tokens": ["it", "was", "the"], "visual": "wayne_quote_video", "subcaption": "Ronald Wayne"},
    {"caption": "RIGHT PRODUCT • RIGHT TIME", "anchor_phrase": "right product at the right time", "tokens": ["right", "product", "at", "the", "right", "time"], "visual": "wayne_quote_video", "subcaption": "His own words"},
    {"caption": "HE EXPECTED…", "anchor_phrase": "he left because he expected", "tokens": ["he", "left", "because", "he", "expected"], "visual": "paperwork_setup", "subcaption": "The life he expected"},
    {"caption": "DECADES OF PAPERWORK", "anchor_phrase": "decades of paperwork", "tokens": ["decades", "of", "paperwork"], "visual": "paperwork", "subcaption": "Administration"},
    {"caption": "INSTEAD OF BUILDING", "anchor_phrase": "instead of building", "tokens": ["instead", "of", "building"], "visual": "building", "subcaption": "He wanted to create"},
    {"caption": "HIS OWN INVENTIONS", "anchor_phrase": "his own inventions", "tokens": ["his", "own", "inventions"], "visual": "inventions", "subcaption": "His chosen work"},
    {"caption": "HIS OWN INVENTIONS", "anchor_phrase": "", "tokens": [], "visual": "inventions_hold", "subcaption": "A different path", "mode": "hold"},
    {"caption": "LOCK YOUR VERDICT", "anchor_phrase": "lock your verdict", "tokens": ["lock", "your", "verdict"], "visual": "verdict_setup", "subcaption": "Before the payoff"},
    {"caption": "SELL OR STAY?", "anchor_phrase": "sell or stay", "tokens": ["sell", "or", "stay"], "visual": "sell_stay_split", "subcaption": "Choose one"},
    {"caption": "LIKE • SUBSCRIBE • COMMENT", "anchor_phrase": "like subscribe and comment", "tokens": ["like", "subscribe", "and", "comment"], "visual": "cta", "subcaption": "Then tell us why"},
    {"caption": "WAYNE SAYS…", "anchor_phrase": "wayne says", "tokens": ["wayne", "says"], "visual": "wayne_says", "subcaption": "His later view"},
    {"caption": "NO REGRET LEAVING APPLE", "anchor_phrase": "not regret leaving apple", "tokens": ["not", "regret", "leaving", "apple"], "visual": "no_regret", "subcaption": "Leaving was not it"},
    {"caption": "WHAT DID HE REGRET?", "anchor_phrase": "what did he regret", "tokens": ["what", "did", "he", "regret"], "visual": "regret_question", "subcaption": "A different decision"},
    {"caption": "ORIGINAL CONTRACT", "anchor_phrase": "original contract", "tokens": ["original", "contract"], "visual": "original_contract", "subcaption": "The partnership document"},
    {"caption": "SOLD FOR $500", "anchor_phrase": "five hundred dollars", "tokens": ["500"], "visual": "money_500", "subcaption": "The price he received"},
    {"caption": "IN 2011…", "anchor_phrase": "in twenty eleven", "tokens": ["in", "2011"], "visual": "auction_2011", "subcaption": "The later auction"},
    {"caption": "SOLD FOR $1.59 MILLION", "anchor_phrase": "one point five nine million", "tokens": ["1", "59", "million"], "visual": "auction_1_59m", "subcaption": "Sotheby's sale"},
    {"caption": "THAT, I REGRET", "anchor_phrase": "that i regret", "tokens": ["that", "i", "regret"], "visual": "direct_quote_regret", "subcaption": "Ronald Wayne"},
    {"caption": "SO WAS HE…", "anchor_phrase": "so was he", "tokens": ["so", "was", "he"], "visual": "verdict_setup", "subcaption": "Judge the decision"},
    {"caption": "HISTORY'S BIGGEST FOOL?", "anchor_phrase": "history's biggest fool", "tokens": ["history's", "biggest", "fool"], "visual": "fool_free_split", "subcaption": "Or rational risk?"},
    {"caption": "WALKING AWAY = FREEDOM?", "anchor_phrase": "walking away give him freedom", "tokens": ["walking", "away", "give", "him", "freedom"], "visual": "freedom_close", "subcaption": "Costly mistake—or freedom?"},
]


def normalize_word(text: str) -> str:
    text = text.strip().lower()
    if text == "%":
        return "percent"
    return re.sub(r"[^a-z0-9']+", "", text)


def load_words(asr: dict[str, Any]) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    for segment in asr.get("segments", []):
        for raw in segment.get("words", []):
            token = normalize_word(str(raw.get("word", "")))
            if token:
                words.append({"token": token, "start": float(raw["start"]), "end": float(raw["end"]), "raw": raw.get("word", "")})
    return words


def find_phrase_start(words: list[dict[str, Any]], tokens: list[str]) -> float:
    wanted = [normalize_word(token) for token in tokens]
    haystack = [word["token"] for word in words]
    for index in range(len(haystack) - len(wanted) + 1):
        if haystack[index : index + len(wanted)] == wanted:
            return float(words[index]["start"])
    raise ValueError(f"ASR anchor not found: {' '.join(tokens)}")


def ceil_to_frame(seconds: float, fps: int = FPS) -> float:
    return math.ceil((seconds - 1e-9) * fps) / fps


def build_sync_beats(asr: dict[str, Any]) -> list[dict[str, Any]]:
    if len(BEAT_SPECS) != 40:
        raise ValueError(f"Expected 40 beat specs, got {len(BEAT_SPECS)}")
    words = load_words(asr)
    beats: list[dict[str, Any]] = []
    for index, spec in enumerate(BEAT_SPECS):
        start = index * BEAT_DURATION
        end = (index + 1) * BEAT_DURATION
        mode = spec.get("mode", "aligned")
        if mode == "hold":
            anchor_start = None
            caption_at = start
        else:
            anchor_start = find_phrase_start(words, spec["tokens"])
            caption_at = max(start, ceil_to_frame(anchor_start))
            if caption_at >= end:
                raise ValueError(
                    f"Beat {index:02d} anchor {anchor_start:.3f}s resolves outside {start:.3f}-{end:.3f}s"
                )
        beats.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "duration": BEAT_DURATION,
                "caption": spec["caption"],
                "subcaption": spec["subcaption"],
                "visual": spec["visual"],
                "mode": mode,
                "anchor_phrase": spec["anchor_phrase"],
                "anchor_start": anchor_start,
                "caption_at": caption_at,
                "caption_delay": caption_at - start,
                "lead_seconds": None if anchor_start is None else caption_at - anchor_start,
            }
        )
    return beats


def write_manifest(asr_path: Path, output_path: Path) -> list[dict[str, Any]]:
    asr = json.loads(asr_path.read_text(encoding="utf-8"))
    beats = build_sync_beats(asr)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(beats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return beats


def validate_manifest(beats: list[dict[str, Any]]) -> dict[str, Any]:
    anchored = [beat for beat in beats if beat["mode"] != "hold"]
    errors: list[str] = []
    if len(beats) != 40:
        errors.append(f"beat_count={len(beats)}")
    for beat in beats:
        index = beat["index"]
        if abs(beat["start"] - index * BEAT_DURATION) > 1e-9:
            errors.append(f"beat_{index:02d}_bad_start")
        if abs(beat["duration"] - BEAT_DURATION) > 1e-9:
            errors.append(f"beat_{index:02d}_bad_duration")
        if not (beat["start"] <= beat["caption_at"] < beat["end"]):
            errors.append(f"beat_{index:02d}_caption_outside")
        if abs(beat["caption_delay"] * FPS - round(beat["caption_delay"] * FPS)) > 1e-7:
            errors.append(f"beat_{index:02d}_not_frame_safe")
        if beat["lead_seconds"] is not None and beat["lead_seconds"] < -1e-9:
            errors.append(f"beat_{index:02d}_caption_leads_audio")
    return {
        "status": "pass" if not errors else "fail",
        "beat_count": len(beats),
        "anchored_beat_count": len(anchored),
        "hold_beat_count": len(beats) - len(anchored),
        "max_caption_lag_seconds": max(beat["lead_seconds"] for beat in anchored),
        "min_caption_lag_seconds": min(beat["lead_seconds"] for beat in anchored),
        "premature_caption_count": sum(1 for beat in anchored if beat["lead_seconds"] < -1e-9),
        "errors": errors,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    asr_path = root / "output/projects/ronaldwayne/checks-v2-qwen/final-asr/final.json"
    output_path = root / "output/projects/ronaldwayne/scripts/visual-edl-v3-qwen-synced.json"
    audit_path = root / "output/projects/ronaldwayne/checks-v3-sync/alignment-audit.json"
    beats = write_manifest(asr_path, output_path)
    audit = validate_manifest(beats)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps({"summary": audit, "beats": beats}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if audit["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
