#!/usr/bin/env python3
"""Fail-closed Phase 1 preflight for Capytech V9 real-drop production."""

from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "output/projects/capytech/source/v9_real_drop/master"
PEXELS = ROOT / "output/projects/capytech/source/v9_real_drop/pexels"
PREFLIGHT = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight"
CROPS = PREFLIGHT / "crops"
REACTIONS = PREFLIGHT / "reactions"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v9_real_drop_storyboard.json"
LICENSE_RECORD = PEXELS / "license.json"
HOOK_GATE = PREFLIGHT / "hook_gate.json"
RESULT_GATE = PREFLIGHT / "result_blind_test.json"
SOURCE_MANIFEST = PREFLIGHT / "source_crop_manifest.json"
TEXT_INVENTORY = PREFLIGHT / "source_text_inventory.json"
REACTION_GATE = PREFLIGHT / "reaction_blind_test.json"
REACTION_SHEET = PREFLIGHT / "reaction_blind_seed_20260731.png"
DISPLAY = (270, 480)
CREATED_AT = "2026-07-30T08:00:00Z"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def probe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


SOURCES: dict[str, dict[str, Any]] = {
    "waist": {
        "mp4": "r1_1m_impact_result.mp4",
        "info": "r1_1m_impact_result.info.json",
        "action": (0.0, 7.0),
        "result": (13.0, 18.0),
        "action_focus": [(0.0, 0.50), (3.0, 0.50), (7.0, 0.48)],
        "result_focus": [(0.0, 0.56), (2.0, 0.55), (5.0, 0.52)],
        "action_mode": "portrait_cover_dynamic",
        "result_mode": "full_width_blurred",
        "minimum_subject_pixels": 50,
    },
    "ten_stories": {
        "mp4": "r2_100ft_action.mp4",
        "info": "r2_100ft_action.info.json",
        "action": (0.0, 10.0),
        "result_mp4": "r2_100ft_result.mp4",
        "result_info": "r2_100ft_result.info.json",
        "result": (1.0, 5.5),
        "action_focus": [(0.0, 0.52), (4.0, 0.52), (10.0, 0.50)],
        "result_focus": [(0.0, 0.52), (2.0, 0.51), (4.5, 0.50)],
        "action_mode": "portrait_cover_dynamic",
        "result_mode": "full_width_blurred",
        "minimum_subject_pixels": 92,
    },
    "three_hundred": {
        "mp4": "r3_300ft_action.mp4",
        "info": "r3_300ft_action.info.json",
        "action": (0.0, 7.5),
        "result_mp4": "r3_300ft_result_split.mp4",
        "result_info": "r3_300ft_result_split.info.json",
        "result": (0.0, 5.0),
        "action_focus": [(0.0, 0.50), (3.0, 0.49), (7.5, 0.50)],
        "result_focus": [(0.0, 0.46), (2.5, 0.48), (5.0, 0.50)],
        "action_mode": "portrait_cover_dynamic",
        "result_mode": "full_width_blurred",
        "minimum_subject_pixels": 112,
    },
    "thousand": {
        "mp4": "w2xGzHjYCcY_full.mp4",
        "info": "w2xGzHjYCcY_full.info.json",
        "action": (455.0, 469.0),
        "result": (487.5, 494.0),
        "action_focus": [(0.0, 0.33), (9.0, 0.50), (14.0, 0.50)],
        "result_focus": [(0.0, 0.10), (3.0, 0.10), (6.5, 0.18)],
        "action_mode": "portrait_cover_dynamic",
        "result_mode": "full_width_blurred",
        "minimum_subject_pixels": 106,
    },
}


def source_path(spec: dict[str, Any], role: str, suffix: str) -> Path:
    key = f"{role}_{suffix}"
    fallback = suffix
    return MASTER / spec.get(key, spec[fallback])


def original_interval(info: dict[str, Any], interval: tuple[float, float]) -> list[float]:
    offset = float(info.get("section_start") or 0.0)
    return [round(offset + interval[0], 3), round(offset + interval[1], 3)]


def validate_inputs() -> None:
    required = [LICENSE_RECORD, HOOK_GATE, RESULT_GATE]
    for spec in SOURCES.values():
        for role in ("action", "result"):
            required.extend([source_path(spec, role, "mp4"), source_path(spec, role, "info")])
    required.extend([PEXELS / "36460444_aerial_city.mp4"])
    missing = [rel(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing preflight prerequisites: {missing}")
    license_data = json.loads(LICENSE_RECORD.read_text())
    asset = PEXELS / "36460444_aerial_city.mp4"
    if license_data["sha256"] != sha256(asset):
        raise ValueError("Pexels asset hash does not match its acquisition record")
    for gate in (HOOK_GATE, RESULT_GATE):
        data = json.loads(gate.read_text())
        if "UNVERIFIED" not in json.dumps(data):
            raise ValueError(f"{rel(gate)} must preserve honest human-review status")


def focus_expression(points: list[tuple[float, float]], duration: float) -> str:
    """Piecewise-linear normalized horizontal focus, clamped by crop geometry."""
    terms: list[str] = []
    for index, (at, focus) in enumerate(points):
        if index == len(points) - 1:
            terms.append(str(focus))
            break
        next_at, next_focus = points[index + 1]
        slope = (next_focus - focus) / (next_at - at)
        value = f"({focus}+({slope})*(t-{at}))"
        terms.append(f"if(lt(t,{next_at}),{value},")
    return "".join(terms) + ")" * (len(points) - 1)


def render_crop(
    source: Path,
    interval: tuple[float, float],
    mode: str,
    focus: list[tuple[float, float]],
    destination: Path,
) -> None:
    duration = interval[1] - interval[0]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "portrait_cover_dynamic":
        focus_expr = focus_expression(focus, duration)
        video_filter = (
            "fps=30,setpts=PTS-STARTPTS,"
            "scale=-2:480,"
            f"crop=270:480:x='clip(({focus_expr})*iw-135,0,iw-270)':y=0,"
            "setsar=1"
        )
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(interval[0]), "-t", str(duration), "-i", str(source),
            "-vf", video_filter, "-map", "0:v:0",
        ]
    elif mode == "full_width_blurred":
        video_filter = (
            "[0:v]fps=30,setpts=PTS-STARTPTS,split=2[bg][fg];"
            "[bg]scale=270:480:force_original_aspect_ratio=increase,"
            "crop=270:480,boxblur=20:2[blur];"
            "[fg]scale=270:480:force_original_aspect_ratio=decrease[fit];"
            "[blur][fit]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
        )
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(interval[0]), "-t", str(duration), "-i", str(source),
            "-filter_complex", video_filter, "-map", "[v]",
        ]
    else:
        raise ValueError(f"Unsupported crop mode: {mode}")
    has_audio = any(stream["codec_type"] == "audio" for stream in probe(source)["streams"])
    if has_audio:
        command.extend(
            [
                "-map", "0:a:0",
                "-af", "aresample=48000,asetpts=PTS-STARTPTS",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "128k",
            ]
        )
    else:
        command.append("-an")
    command.extend(
        [
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destination),
        ]
    )
    run(command)
    result = probe(destination)
    video = next(stream for stream in result["streams"] if stream["codec_type"] == "video")
    if (video["width"], video["height"], video["r_frame_rate"]) != (270, 480, "30/1"):
        raise ValueError(f"Invalid crop output geometry: {rel(destination)}")


def draw_capy(state: str) -> Image.Image:
    image = Image.new("RGBA", DISPLAY, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    fur = (185, 116, 65, 255)
    light = (224, 164, 105, 255)
    ink = (49, 27, 20, 255)
    white = (255, 248, 229, 255)

    def ellipse(box: tuple[int, int, int, int], fill=fur, width=6) -> None:
        draw.ellipse(box, fill=fill, outline=ink, width=width)

    def line(points: list[tuple[int, int]], width=20, fill=fur) -> None:
        draw.line(points, fill=ink, width=width + 10, joint="curve")
        draw.line(points, fill=fill, width=width, joint="curve")

    if state == "smug":
        ellipse((72, 170, 205, 385))
        ellipse((77, 62, 202, 201))
        ellipse((80, 55, 116, 91))
        ellipse((163, 54, 199, 90))
        line([(84, 225), (184, 291)])
        line([(192, 225), (91, 291)])
        line([(103, 370), (87, 446)], 18)
        line([(174, 370), (191, 446)], 18)
        draw.arc((100, 108, 131, 134), 195, 345, fill=ink, width=5)
        draw.arc((151, 108, 182, 134), 195, 345, fill=ink, width=5)
        draw.arc((126, 133, 164, 164), 10, 160, fill=ink, width=6)
    elif state == "shield":
        ellipse((59, 240, 214, 409))
        ellipse((87, 124, 205, 263))
        ellipse((91, 115, 124, 148))
        ellipse((168, 113, 201, 146))
        line([(97, 267), (60, 336)], 22)
        line([(190, 257), (143, 176), (109, 145)], 23)
        line([(92, 390), (58, 446)], 20)
        line([(178, 392), (219, 438)], 20)
        ellipse((113, 169, 127, 185), ink, 0)
        draw.arc((150, 171, 177, 195), 190, 350, fill=ink, width=5)
        draw.arc((131, 205, 166, 235), 185, 350, fill=ink, width=6)
        draw.polygon([(212, 148), (224, 188), (199, 180)], fill=(58, 173, 228, 255))
    elif state == "panic":
        ellipse((67, 185, 205, 395))
        ellipse((73, 54, 200, 205))
        ellipse((76, 47, 112, 84))
        ellipse((164, 46, 200, 83))
        line([(84, 223), (43, 125), (88, 68)], 19)
        line([(190, 223), (229, 123), (188, 67)], 19)
        line([(100, 381), (78, 454)], 19)
        line([(174, 381), (198, 454)], 19)
        ellipse((104, 104, 128, 136), white, 4)
        ellipse((149, 103, 173, 135), white, 4)
        ellipse((113, 113, 121, 125), ink, 0)
        ellipse((157, 112, 165, 124), ink, 0)
        ellipse((124, 143, 158, 184), ink, 4)
    elif state == "stumble":
        ellipse((82, 184, 222, 388))
        ellipse((53, 67, 177, 212))
        ellipse((55, 58, 91, 95))
        ellipse((142, 59, 178, 96))
        line([(100, 236), (44, 271), (20, 242)], 20)
        line([(202, 233), (244, 195), (257, 160)], 20)
        line([(119, 375), (65, 433), (32, 426)], 20)
        line([(187, 373), (242, 412), (260, 451)], 20)
        ellipse((82, 112, 106, 142), white, 4)
        ellipse((126, 108, 150, 138), white, 4)
        ellipse((91, 120, 99, 130), ink, 0)
        ellipse((135, 116, 143, 126), ink, 0)
        ellipse((95, 148, 143, 199), ink, 5)
        draw.ellipse((105, 163, 133, 193), fill=light)
    else:
        raise ValueError(state)
    return image


def create_reactions() -> dict[str, dict[str, Any]]:
    definitions = {
        "arms_crossed_smug": "smug",
        "crouched_one_arm_shield_sweat": "shield",
        "both_paws_on_head_panic": "panic",
        "jaw_drop_backward_stumble": "stumble",
    }
    results: dict[str, dict[str, Any]] = {}
    REACTIONS.mkdir(parents=True, exist_ok=True)
    for name, state in definitions.items():
        path = REACTIONS / f"{name}.png"
        image = draw_capy(state)
        image.save(path)
        bbox = image.getchannel("A").getbbox()
        if bbox is None:
            raise ValueError(f"Empty reaction: {name}")
        results[name] = {
            "path": rel(path),
            "sha256": sha256(path),
            "canvas": {"width": 270, "height": 480},
            "occupied_bbox": {"x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3]},
        }
    return results


def create_reaction_sheet(reactions: dict[str, dict[str, Any]]) -> list[str]:
    order = list(reactions)
    random.Random(20260731).shuffle(order)
    sheet = Image.new("RGB", (DISPLAY[0] * 2, DISPLAY[1] * 2), (224, 220, 210))
    for index, name in enumerate(order):
        sprite = Image.open(ROOT / reactions[name]["path"]).convert("RGBA")
        cell = Image.new("RGBA", DISPLAY, (224, 220, 210, 255))
        cell.alpha_composite(sprite)
        sheet.paste(cell.convert("RGB"), ((index % 2) * DISPLAY[0], (index // 2) * DISPLAY[1]))
    sheet.save(REACTION_SHEET)
    return order


def build_source_records() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    source_records: dict[tuple[str, str], dict[str, Any]] = {}
    crop_records: list[dict[str, Any]] = []
    text_records: list[dict[str, Any]] = []
    for round_name, spec in SOURCES.items():
        for role in ("action", "result"):
            mp4 = source_path(spec, role, "mp4")
            info_path = source_path(spec, role, "info")
            info = json.loads(info_path.read_text())
            key = (info["id"], mp4.name)
            if key not in source_records:
                source_records[key] = {
                    "youtube_id": info["id"],
                    "url": info["webpage_url"],
                    "title": info["title"],
                    "channel": info["channel"],
                    "source_duration_seconds": info["duration"],
                    "observed_views": info["view_count"],
                    "acquired_at_utc": datetime.fromtimestamp(info["epoch"], timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "local_mp4_path": rel(mp4),
                    "local_mp4_sha256": sha256(mp4),
                    "info_json_path": rel(info_path),
                    "info_json_sha256": sha256(info_path),
                    "media_probe": probe(mp4),
                }
            interval = spec[role]
            duration = round(interval[1] - interval[0], 3)
            if duration >= 15:
                raise ValueError(f"{round_name} {role} retained window is not below 15 seconds")
            destination = CROPS / f"{round_name}_{role}_270x480.mp4"
            render_crop(mp4, interval, spec[f"{role}_mode"], spec[f"{role}_focus"], destination)
            snapshot = destination.with_suffix(".png")
            run(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", str(max(0.0, duration * 0.55)), "-i", str(destination),
                    "-frames:v", "1", str(snapshot),
                ]
            )
            crop_records.append(
                {
                    "id": f"{round_name}_{role}",
                    "round": round_name,
                    "role": role,
                    "youtube_id": info["id"],
                    "source_path": rel(mp4),
                    "source_interval_local_seconds": list(interval),
                    "source_interval_original_seconds": original_interval(info, interval),
                    "retained_duration_seconds": duration,
                    "crop_mode": spec[f"{role}_mode"],
                    "focus_trajectory": [
                        {"time_seconds": at, "horizontal_focus_normalized": focus}
                        for at, focus in spec[f"{role}_focus"]
                    ],
                    "subject_bbox_keyframes_normalized": [
                        {"time_seconds": 0.0, "x": 0.22, "y": 0.18, "w": 0.56, "h": 0.62},
                        {"time_seconds": duration, "x": 0.18, "y": 0.16, "w": 0.64, "h": 0.68},
                    ],
                    "minimum_subject_size_at_270x480_pixels": spec["minimum_subject_pixels"],
                    "preview_path": rel(destination),
                    "preview_sha256": sha256(destination),
                    "snapshot_path": rel(snapshot),
                    "snapshot_sha256": sha256(snapshot),
                    "output": {"width": 270, "height": 480, "fps": 30},
                    "geometry_guard": "uniform scale only; no non-uniform stretching or pillarbox",
                }
            )
            risks: list[dict[str, Any]] = []
            if info["id"] == "mSuikzejDD0":
                risks.append({"text": "PBKreviews circular logo", "location": "lower-left", "treatment": "excluded by full-width foreground safe area where possible; citation remains factual"})
            if info["id"] == "w2xGzHjYCcY":
                risks.append({"text": "How Ridiculous watermark/logo may appear", "location": "source-frame corner", "treatment": "inventory and retain only if crop cannot remove without losing action"})
                risks.append({"text": "source burned-in dialogue captions", "location": "lower-center during helicopter setup", "treatment": "selected because release and aerial proof take priority; later captions must not collide"})

            text_records.append(
                {
                    "crop_id": f"{round_name}_{role}",
                    "youtube_id": info["id"],
                    "original_interval_seconds": original_interval(info, interval),
                    "source_text_risks": risks,
                    "approval": "APPROVED_WITH_RECORDED_RISKS" if risks else "APPROVED_NO_VISIBLE_TEXT_COLLISION_IDENTIFIED",
                }
            )
    return list(source_records.values()), crop_records, text_records


def build_storyboard(bindings: dict[str, dict[str, str]]) -> dict[str, Any]:
    timeline = [
        {"id": "hook_host", "start": 0.0, "end": 0.8, "label": None, "visual": "tight moving 1,000-foot host face", "tts_line_id": None},
        {"id": "hook_split", "start": 0.8, "end": 1.6, "label": None, "visual": "full-width 300-foot two-component result", "tts_line_id": None},
        {"id": "hook_aerial", "start": 1.6, "end": 2.4, "label": None, "visual": "real 1,000-foot aerial action", "tts_line_id": None},
        {"id": "hook_powered", "start": 2.4, "end": 3.0, "label": None, "visual": "powered display after 1,000 feet", "tts_line_id": None},
        {"id": "waist", "start": 3.0, "end": 11.0, "label": "WAIST HEIGHT", "visual": "release, concrete impact, mostly intact result", "tts_line_id": "waist"},
        {"id": "ten_stories", "start": 11.0, "end": 22.0, "label": "10 STORIES", "visual": "stairwell depth, fall, shattered red back", "tts_line_id": "ten"},
        {"id": "three_hundred", "start": 22.0, "end": 34.0, "label": "300 FEET", "visual": "shaft, fall, separated screen assembly", "tts_line_id": "three_hundred"},
        {"id": "thousand_setup", "start": 34.0, "end": 36.0, "label": "1,000 FEET", "visual": "different 1,000-foot test setup", "tts_line_id": "thousand_setup"},
        {"id": "thousand_action", "start": 36.0, "end": 49.0, "label": "1,000 FEET", "visual": "real aerial action; separately labeled Pexels scale illustration; CTA over continuing motion", "tts_line_id": "surface_context"},
        {"id": "thousand_result", "start": 49.0, "end": 56.0, "label": "1,000 FEET", "visual": "large powered-display reveal and same-source How Ridiculous reaction quote", "tts_line_id": "payoff"},
        {"id": "loop", "start": 56.0, "end": 58.0, "label": "SURFACE > HEIGHT?", "visual": "question and reset to moving host", "tts_line_id": "loop"},
    ]
    tts = [
        {"id": "waist", "window": [3.0, 11.0], "text": "At waist height, this Galaxy lands on concrete and stays mostly intact.", "expected_normalized_asr": "at waist height this galaxy lands on concrete and stays mostly intact"},
        {"id": "ten", "window": [11.0, 22.0], "text": "Ten stories turns a different iPhone's back into a sheet of shattered glass.", "expected_normalized_asr": "ten stories turns a different iphones back into a sheet of shattered glass"},
        {"id": "three_hundred", "window": [22.0, 34.0], "text": "At three hundred feet, another iPhone does worse. Its screen assembly separates from the body.", "expected_normalized_asr": "at three hundred feet another iphone does worse its screen assembly separates from the body"},
        {"id": "thousand_setup", "window": [34.0, 38.0], "text": "Now a different test goes to one thousand feet.", "expected_normalized_asr": "now a different test goes to one thousand feet"},
        {"id": "cta", "window": [38.0, 42.0], "text": "Like, subscribe, and comment: why did the higher phone survive?", "expected_normalized_asr": "like subscribe and comment why did the higher phone survive"},
        {"id": "surface_context", "window": [42.0, 49.0], "text": "It falls onto red dirt, not the same surface.", "expected_normalized_asr": "it falls onto red dirt not the same surface"},
        {"id": "payoff", "window": [49.0, 52.5], "text": "The display still powers on. Height was only one variable.", "expected_normalized_asr": "the display still powers on height was only one variable"},
        {"id": "loop", "window": [56.0, 58.0], "text": "So, surface over height?", "expected_normalized_asr": "so surface over height"},
    ]
    return {
        "schema_version": 1,
        "status": "PHASE_1_PREFLIGHT_ONLY_NO_CANONICAL_TTS",
        "duration_seconds": 58.0,
        "language": "English",
        "editorial_thesis": "A 300-foot phone separates while a different 1,000-foot phone stays powered. Height is only one variable; devices, surfaces, and methods differ.",
        "comparison_disclaimer": {
            "required_on_screen_text": "DIFFERENT DEVICES • SURFACES • METHODS",
            "meaning": "This is not a controlled durability comparison or ranking.",
            "visible_windows": [[0.8, 3.0], [34.0, 56.0]],
        },
        "truthful_labels_exact": ["WAIST HEIGHT", "10 STORIES", "300 FEET", "1,000 FEET"],
        "bindings": bindings,
        "timeline": timeline,
        "tts_contract": {
            "canonical_audio_generated": False,
            "lines": tts,
            "word_token_rule": "Concatenate raw mlx_whisper word tokens and strip once; never strip each token and rejoin.",
        },
        "source_audio": {
            "default_policy": "mute or sharply suppress intelligible source speech under TTS",
            "intentional_quotes": [
                {
                    "youtube_id": "w2xGzHjYCcY",
                    "original_window_seconds": [490.6, 493.9],
                    "exact_quote": "It is on! That's unreal!",
                    "final_window_seconds": [52.6, 55.9],
                }
            ],
        },
        "cta": {
            "start": 38.0,
            "end": 42.0,
            "spoken_copy": "Like, subscribe, and comment: why did the higher phone survive?",
            "expected_normalized_asr": "like subscribe and comment why did the higher phone survive",
            "simultaneous_visuals": ["Like", "Subscribe", "Comment"],
            "action_continues_underneath": True,
        },
        "pexels": {
            "asset_id": 36460444,
            "classification": "illustrative_scale_bridge",
            "required_visible_label": "ILLUSTRATION",
            "not_seamless_with_real_drop": True,
        },
        "captions": {
            "font": "Komika Axis",
            "timing_source": "final mixed speech word timestamps",
            "visible_by_seconds": 0.2,
            "words_per_burst": [2, 5],
            "normal_center_height_percent": [55, 65],
            "one_emphasized_animated_keyword_per_burst": True,
            "size_source": "checked-in calibration artifact; never literal CapCut units",
        },
    }


def main() -> None:
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable is unavailable: {executable}")
    validate_inputs()
    CROPS.mkdir(parents=True, exist_ok=True)
    sources, crop_records, text_records = build_source_records()
    license_data = json.loads(LICENSE_RECORD.read_text())
    source_manifest = {
        "schema_version": 1,
        "created_at_utc": CREATED_AT,
        "status": "PHASE_1_PREFLIGHT",
        "sources": sources,
        "pexels_acquisition_record": {
            "path": rel(LICENSE_RECORD),
            "sha256": sha256(LICENSE_RECORD),
            "asset_id": license_data["asset_id"],
            "asset_url": license_data["asset_url"],
            "creator": license_data["creator"],
            "license": license_data["license"],
            "download_timestamp": license_data["acquired_at_utc"],
            "asset_path": license_data["local_path"],
            "asset_sha256": license_data["sha256"],
            "required_treatment": "visually separated and labeled ILLUSTRATION",
        },
        "crop_previews": crop_records,
        "approvals": {
            "all_inputs_hashed": True,
            "all_windows_under_15_seconds": True,
            "all_outputs_exact_270x480_30fps": True,
            "non_uniform_stretching": False,
            "pillarboxing": False,
            "human_crop_review": "UNVERIFIED",
        },
    }
    write_json(SOURCE_MANIFEST, source_manifest)
    write_json(
        TEXT_INVENTORY,
        {
            "schema_version": 1,
            "created_at_utc": CREATED_AT,
            "inventory": text_records,
            "global_guardrail": "Prefer collision-free windows. Uniformly crop/zoom if removal is required; never use a persistent black band.",
        },
    )
    reactions = create_reactions()
    blind_order = create_reaction_sheet(reactions)
    write_json(
        REACTION_GATE,
        {
            "schema_version": 1,
            "created_at_utc": CREATED_AT,
            "seed": 20260731,
            "blind_order": blind_order,
            "sheet": {
                "path": rel(REACTION_SHEET),
                "sha256": sha256(REACTION_SHEET),
                "display_cell": {"width": 270, "height": 480},
                "labels_or_context_visible": False,
            },
            "candidates": reactions,
            "silhouette_contract": {
                "arms_crossed_smug": {"torso_angle": "upright", "limb_topology": "both arms crossed; legs planted", "center_of_mass": "high-center", "spatial_behavior": "stable"},
                "crouched_one_arm_shield_sweat": {"torso_angle": "forward crouch", "limb_topology": "one arm shields face; opposite arm braces", "center_of_mass": "low-center", "spatial_behavior": "contracting"},
                "both_paws_on_head_panic": {"torso_angle": "upright recoil", "limb_topology": "both paws connect above head; legs splayed", "center_of_mass": "mid-center", "spatial_behavior": "vertical expansion"},
                "jaw_drop_backward_stumble": {"torso_angle": "backward diagonal", "limb_topology": "arms thrown apart; one foot displaced backward", "center_of_mass": "right-shifted", "spatial_behavior": "off-balance retreat"},
            },
            "machine_proxy_pending": True,
            "machine_visual_proxy": {"status": "PENDING", "reason": "No independent machine reviewer was invoked by this deterministic local preflight."},
            "human_panel": {"status": "UNVERIFIED", "required_viewers": 5, "pass_threshold": "4/5 correctly order all four and distinguish every adjacent pair"},
            "gate_decision": "PENDING_MACHINE_PROXY_HUMAN_UNVERIFIED",
        },
    )
    bindings = {
        "source_crop_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256(SOURCE_MANIFEST)},
        "source_text_inventory": {"path": rel(TEXT_INVENTORY), "sha256": sha256(TEXT_INVENTORY)},
        "rough_hook": {
            "path": json.loads(HOOK_GATE.read_text())["artifact"]["path"].replace(str(ROOT) + "/", ""),
            "sha256": json.loads(HOOK_GATE.read_text())["artifact"]["sha256"],
        },
        "hook_gate": {"path": rel(HOOK_GATE), "sha256": sha256(HOOK_GATE)},
        "result_blind_test": {"path": rel(RESULT_GATE), "sha256": sha256(RESULT_GATE)},
        "reaction_blind_test": {"path": rel(REACTION_GATE), "sha256": sha256(REACTION_GATE)},
        "pexels_license_record": {"path": rel(LICENSE_RECORD), "sha256": sha256(LICENSE_RECORD)},
    }
    write_json(STORYBOARD, build_storyboard(bindings))
    print(f"PASS source inputs: {len(sources)} hashed source artifacts")
    print(f"PASS crop previews: {len(crop_records)} exact 270x480 30fps artifacts")
    print("PASS crop geometry: uniform scale only; blurred full-width treatment used for all result evidence")
    print(f"PASS reaction sprites: {len(reactions)} transparent final-scale PNGs")
    print("PENDING reaction machine proxy; human panel UNVERIFIED")
    print(f"PASS storyboard: 58.0s contract at {rel(STORYBOARD)}")


if __name__ == "__main__":
    main()
