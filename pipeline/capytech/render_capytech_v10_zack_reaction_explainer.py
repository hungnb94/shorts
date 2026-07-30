#!/usr/bin/env python3
"""Render the V10 base master from locked native sources and canonical TTS.

The renderer creates its reaction drawings at 1080x1920. It never reads the
V9 270x480 proxy reactions. Citations and the mechanism card remain a separate
post-render value-add stage.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v10_zack_reaction_explainer_storyboard.json"
SOURCE_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json"
PEXELS_LICENSE = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/license.json"
PEXELS = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/36460444_aerial_city.mp4"
PROFILE = ROOT / "data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json"
TTS_GENERATOR = ROOT / "pipeline/capytech/generate_capytech_v10_zack_tts.py"
TTS_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v10_zack_reaction_explainer_work/audio/tts_manifest.json"
WORK = ROOT / "output/projects/capytech/clips/capytech_v10_zack_reaction_explainer_work"
REACTIONS = WORK / "reaction_assets_native"
SEGMENTS = WORK / "segments"
TRACKS = WORK / "audio/tracks"
AUDIO_ASSETS = WORK / "audio/production_assets"
ASS = WORK / "captions.ass"
BASE = WORK / "base_master.mp4"
RENDER_MANIFEST = WORK / "render_manifest.json"
SOURCE_USAGE = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/source_usage.json"
REACTION_GATE = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/reaction_asset_manifest.json"
IMPLEMENTATION_REVIEW = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/codex_implementation_review.json"
STAGE0 = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/stage0"
STAGE0_PREVIEW = STAGE0 / "capytech_v10_zack_hook_0.0-5.0.mp4"
STAGE0_MANIFEST = STAGE0 / "hook_manifest.json"
STAGE0_REVIEW = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/stage0_external_naive_view.json"
PREFLIGHT = ROOT / "pipeline/capytech/preflight_capytech_v10_zack_hook.py"
COMPOSITOR = ROOT / "pipeline/capytech/composite_capytech_v10_value_adds.py"
VERIFIER = ROOT / "pipeline/capytech/verify_capytech_v10_zack_reaction_explainer.py"
FONT = ROOT / "assets/fonts/Komika-Axis.ttf"
CALIBRATION = ROOT / "docs/verification/caption-calibration/caption-profile.json"
SYNTH_LOCK = ROOT / "spikes/001-english-tts-engine-bakeoff/requirements-mlx.txt"
DURATION, FPS, RATE = 58.0, 30, 48_000
PROFILE_SHA256 = "ea056c484bc075495fb696887390c32028e54ea5759f7379e6680545914d4408"
REFERENCE_SHA256 = "73550032e52f99f02230d2bd0ca656b8627d936d086889a6534d51dc9541ca09"
MODEL_REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit"
MODEL_REVISION = "34ff5318365b59cba9c03ff729f2eee0814caf72"
WEIGHTS = {
    "model.safetensors": "b043693cb63f38f4e0ae5fe39a5cfdb466ef199dc5a767991a4a46235ac27e67",
    "speech_tokenizer/model.safetensors": "836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258",
}
APPROVED_GENERATION_SETTINGS = {
    "language": "English", "temperature": 0.7, "max_tokens": 768,
    "top_k": 30, "top_p": 0.9, "repetition_penalty": 1.5,
}
V10_FFMPEG_FINGERPRINT = {
    "version_line": "ffmpeg version 7.1.1 Copyright (c) 2000-2025 the FFmpeg developers",
    "version_output_sha256": "88b12a030360dd4614c0e3999e442dd5cfa63c6df2b7b8dc2f23f56a40399ff9",
}


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


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=capture)


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected:
        raise RuntimeError(f"{label} missing or hash mismatch: {path}")


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
        "name": "synthesis",
        "python": expected["python"],
        "python_implementation": "cpython",
        "lock_file": expected["lock_file"],
        "lock_sha256": lock_sha,
        "packages": dict(sorted(packages.items())),
    }


def validate_inputs(
    require_stage0_review: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    storyboard, sources, tts = load(STORYBOARD), load(SOURCE_MANIFEST), load(TTS_MANIFEST)
    bindings = storyboard["bindings"]
    require_hash(SOURCE_MANIFEST, bindings["source_crop_manifest"]["sha256"], "V9 source manifest")
    require_hash(PEXELS_LICENSE, bindings["pexels_license"]["sha256"], "Pexels license")
    require_hash(PEXELS, bindings["pexels_asset"]["sha256"], "Pexels asset")
    require_hash(PROFILE, PROFILE_SHA256, "Zack profile")
    require_hash(TTS_GENERATOR, tts["generator_sha256"], "TTS generator")
    for source in sources["sources"]:
        require_hash(ROOT / source["local_mp4_path"], source["local_mp4_sha256"],
                     f"source media {source['local_mp4_path']}")
        require_hash(ROOT / source["info_json_path"], source["info_json_sha256"],
                     f"source metadata {source['info_json_path']}")
    if tts["storyboard_sha256"] != sha256(STORYBOARD):
        raise RuntimeError("TTS storyboard is stale")
    profile = tts.get("profile", {})
    model = tts.get("model", {})
    fitting = tts.get("fitting_settings", {})
    generation = tts.get("generation_settings", {})
    runtime = tts.get("runtime", {})
    profile_spec = load(PROFILE)
    if (profile.get("id"), profile.get("sha256"), profile.get("reference_sha256")) != (
        "ronald_wayne_zack_style_qwen", PROFILE_SHA256, REFERENCE_SHA256
    ):
        raise RuntimeError("TTS Zack identity contract mismatch")
    if (model.get("repo"), model.get("revision"), model.get("weights")) != (
        MODEL_REPO, MODEL_REVISION, WEIGHTS
    ):
        raise RuntimeError("TTS model repository/revision/weights mismatch")
    if generation != APPROVED_GENERATION_SETTINGS:
        raise RuntimeError("TTS generation settings mismatch")
    if runtime.get("policy") != "V10_REVIEWED_FFMPEG_RUNTIME_OVERRIDE_PROFILE_UNCHANGED" \
            or runtime.get("profile_expected") \
                != profile_spec["runtime"]["repeatability_fingerprints"] \
            or runtime.get("actual", {}).get("ffmpeg") != V10_FFMPEG_FINGERPRINT \
            or runtime.get("actual", {}).get("platform") \
                != profile_spec["runtime"]["repeatability_fingerprints"]["platform"] \
            or runtime.get("synthesis_environment") != expected_synthesis_environment(profile_spec):
        raise RuntimeError("TTS synthesis runtime/provenance mismatch")
    if (fitting.get("engine_label"), fitting.get("cli_version"), fitting.get("version"),
            fitting.get("max_post_tempo"), fitting.get("mode"), fitting.get("command_flag")) != (
                "Rubber Band R3", "4.0.0", "Rubber Band R3 4.0.0", 1.42,
                "R3_FINE", "--fine"):
        raise RuntimeError("TTS fitting engine contract mismatch")
    expected = {line["id"]: line for line in storyboard["tts_contract"]["lines"]}
    if {line["id"] for line in tts["lines"]} != set(expected):
        raise RuntimeError("TTS line set mismatch")
    previous_end = -1.0
    for record in tts["lines"]:
        contract = expected[record["id"]]
        if record["source_text"] != contract["text"] or record["envelope"] != contract["envelope"]:
            raise RuntimeError(f"Stale TTS text/window: {record['id']}")
        measured_tempo = float(record["measured_tempo"])
        if measured_tempo > 1.42:
            raise RuntimeError(f"Illegal tempo: {record['id']}")
        expected_engine = "R3_FINE" if measured_tempo > 1.0 + 1e-6 else "BYPASS_TEMPO_1_0"
        if record.get("tempo_engine_observed") != expected_engine:
            raise RuntimeError(f"Unverified tempo engine: {record['id']}")
        onset, end = float(record["speech_onset_seconds_absolute"]), float(record["speech_end_seconds_absolute"])
        guard_start, guard_end = map(float, contract["speech_guard"])
        if onset < guard_start - 0.03 or end > guard_end + 0.03 or onset < previous_end:
            raise RuntimeError(f"Narration overlap/guard violation: {record['id']}")
        previous_end = end
        require_hash(ROOT / record["path"], record["sha256"], f"TTS {record['id']}")
    implementation_review = require_implementation_review()
    if require_stage0_review:
        require_stage0_external_review()
    return storyboard, sources, tts, implementation_review


def require_implementation_review() -> dict[str, Any]:
    """Fail before any media generation unless the implementation review is current."""
    if not IMPLEMENTATION_REVIEW.is_file():
        raise RuntimeError(f"Missing blocking implementation review: {IMPLEMENTATION_REVIEW}")
    review = load(IMPLEMENTATION_REVIEW)
    parents = {
        "storyboard": STORYBOARD, "generator": TTS_GENERATOR,
        "renderer": Path(__file__).resolve(), "preflight": PREFLIGHT,
        "compositor": COMPOSITOR, "verifier": VERIFIER,
    }
    expected = {name: sha256(path) for name, path in parents.items()}
    if review.get("bindings") != expected:
        raise RuntimeError("Codex implementation review is stale")
    if review.get("status") != "PASS_ACTIONABLE_FINDINGS_APPLIED" \
            or not review.get("reviewer") or review.get("unresolved_actionable_findings"):
        raise RuntimeError("Codex implementation review has not passed")
    return review


def require_stage0_external_review() -> dict[str, Any]:
    """Require a current independent naive-view pass before a full render."""
    if not STAGE0_REVIEW.is_file():
        raise RuntimeError(f"Missing blocking Stage-0 external review: {STAGE0_REVIEW}")
    review = load(STAGE0_REVIEW)
    expected = {
        "hook_preview": sha256(STAGE0_PREVIEW),
        "hook_manifest": sha256(STAGE0_MANIFEST),
        "storyboard": sha256(STORYBOARD),
        "tts_manifest": sha256(TTS_MANIFEST),
        "renderer": sha256(Path(__file__).resolve()),
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
    reviewed_at = str(review.get("reviewed_at_utc", ""))
    try:
        parsed_utc = datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("Stage-0 review has invalid reviewed_at_utc") from exc
    assessment = review.get("assessment", {})
    if review.get("bindings") != expected:
        raise RuntimeError("Stage-0 external review is stale")
    if review.get("status") != "PASS_STAGE0_EXTERNAL_NAIVE_VIEW" \
            or not review.get("reviewer") or not review.get("reviewer_type") \
            or parsed_utc.utcoffset() != timezone.utc.utcoffset(parsed_utc) \
            or set(assessment) != required_assessment or not all(assessment.values()):
        raise RuntimeError("Stage-0 external naive-view review has not passed")
    return review


def native_reaction(name: str, pose: str, center_x: int, center_y: int) -> dict[str, Any]:
    """Draw a distinct native final-canvas pose with stable feet and QC landmarks."""
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    outline, fur, belly, white, mouth = "#20150f", "#b97538", "#e8bb78", "#ffffff", "#41110f"
    specs = {
        "smug": {"torso_dx": 0, "torso_dy": 0, "head_dx": 35, "head_dy": 0,
                 "body_sx": 1.0, "body_sy": 1.0, "eye": 38, "jaw": 0, "paw": "folded"},
        "shield": {"torso_dx": 20, "torso_dy": 95, "head_dx": -45, "head_dy": 45,
                   "body_sx": 1.04, "body_sy": 0.84, "eye": 28, "jaw": 0, "paw": "shield"},
        "read": {"torso_dx": 0, "torso_dy": 0, "head_dx": 0, "head_dy": 0,
                 "body_sx": 1.0, "body_sy": 1.0, "eye": 40, "jaw": 0, "paw": "low"},
        "shock": {"torso_dx": 20, "torso_dy": -10, "head_dx": 5, "head_dy": -20,
                  "body_sx": 1.0, "body_sy": 0.98, "eye": 70, "jaw": 1, "paw": "high"},
        "recoil_one": {"torso_dx": 95, "torso_dy": -30, "head_dx": 130, "head_dy": -30,
                       "body_sx": 0.94, "body_sy": 0.86, "eye": 76, "jaw": 1, "paw": "wide"},
        "recoil_two": {"torso_dx": 145, "torso_dy": -55, "head_dx": 185, "head_dy": -30,
                       "body_sx": 0.88, "body_sy": 0.76, "eye": 82, "jaw": 1, "paw": "wide"},
        "powered_read": {"torso_dx": 0, "torso_dy": 0, "head_dx": 0, "head_dy": 0,
                         "body_sx": 1.0, "body_sy": 1.0, "eye": 40, "jaw": 0, "paw": "low"},
        "powered_eye_pop": {"torso_dx": 20, "torso_dy": -20, "head_dx": 15, "head_dy": -35,
                            "body_sx": 0.98, "body_sy": 0.94, "eye": 82, "jaw": 1, "paw": "high"},
        "powered_recoil": {"torso_dx": 125, "torso_dy": -55, "head_dx": 120, "head_dy": -40,
                           "body_sx": 0.88, "body_sy": 0.77, "eye": 86, "jaw": 1, "paw": "wide"},
    }
    spec = specs[pose]
    foot_y = center_y + 640
    left_foot, right_foot = (center_x - 155, foot_y), (center_x + 155, foot_y)
    torso_cx = center_x + spec["torso_dx"]
    torso_cy = center_y + 95 + spec["torso_dy"]
    head_cx = center_x + spec["head_dx"]
    head_cy = center_y - 430 + spec["head_dy"]
    body_half_w = round(245 * spec["body_sx"])
    body_half_h = round(390 * spec["body_sy"])
    body = (torso_cx - body_half_w, torso_cy - body_half_h,
            torso_cx + body_half_w, torso_cy + body_half_h)
    head = (head_cx - 265, head_cy - 270, head_cx + 265, head_cy + 270)
    if pose in {"recoil_one", "recoil_two", "powered_recoil"}:
        motion_x = 790 if pose == "powered_recoil" else 65
        for line_y, line_w in ((610, 250), (770, 205), (930, 160)):
            draw.line((motion_x, line_y, motion_x + line_w, line_y - 45),
                      fill="#00D7FF", width=18)
        bolt_x = 860 if pose == "powered_recoil" else 45
        draw.polygon([(bolt_x + 70, 430), (bolt_x + 130, 470), (bolt_x + 90, 515),
                      (bolt_x + 175, 550), (bolt_x + 50, 590),
                      (bolt_x + 70, 530), (bolt_x, 500)],
                     fill="#FFD83D", outline=outline)
    draw.ellipse(body, fill=fur, outline=outline, width=26)
    draw.ellipse((torso_cx - round(165 * spec["body_sx"]),
                  torso_cy - round(240 * spec["body_sy"]),
                  torso_cx + round(165 * spec["body_sx"]),
                  torso_cy + round(300 * spec["body_sy"])), fill=belly)
    draw.ellipse(head, fill=fur, outline=outline, width=26)
    eye_radius = spec["eye"]
    squint = pose == "shield"
    eye_y = head_cy - 75
    for ex in (head_cx - 105, head_cx + 105):
        if squint:
            draw.line((ex - 55, eye_y + 10, ex + 55, eye_y - 12), fill=outline, width=24)
            continue
        if pose == "smug":
            draw.arc((ex - eye_radius, eye_y - eye_radius, ex + eye_radius,
                      eye_y + eye_radius), 195, 345, fill=outline, width=18)
            draw.ellipse((ex - 12, eye_y + 2, ex + 12, eye_y + 26), fill=outline)
            continue
        draw.ellipse((ex - eye_radius, eye_y - eye_radius, ex + eye_radius, eye_y + eye_radius),
                     fill=white, outline=outline, width=18)
        draw.ellipse((ex - 18, eye_y - 18, ex + 18, eye_y + 18), fill=outline)
    mouth_y = head_cy + 120
    if spec["jaw"]:
        draw.ellipse((head_cx - 105, mouth_y - 90, head_cx + 105, mouth_y + 110),
                     fill=mouth, outline=outline, width=18)
    elif pose == "smug":
        draw.arc((head_cx - 115, mouth_y - 70, head_cx + 115, mouth_y + 55),
                 350, 165, fill=outline, width=20)
    else:
        draw.arc((head_cx - 100, mouth_y - 55, head_cx + 100, mouth_y + 45),
                 10, 170, fill=outline, width=18)
    wide_extent = 240 if pose == "powered_recoil" else 285 if pose == "recoil_two" else 315
    paw_xys = {
        "folded": ((torso_cx + 115, torso_cy - 30), (torso_cx - 115, torso_cy + 10)),
        "shield": ((head_cx - 185, head_cy + 20), (head_cx + 45, head_cy + 95)),
        "low": ((torso_cx - 305, torso_cy + 40), (torso_cx + 305, torso_cy + 40)),
        "high": ((head_cx - 330, head_cy - 25), (head_cx + 330, head_cy - 25)),
        "wide": ((head_cx - wide_extent, head_cy - 55),
                 (head_cx + wide_extent, head_cy - 55)),
    }[spec["paw"]]
    if pose == "powered_eye_pop":
        paw_xys = ((head_cx - 190, head_cy - 45),
                   (head_cx + 250, head_cy - 45))
    if pose == "smug":
        draw.line((torso_cx - 185, torso_cy - 135, paw_xys[0][0], paw_xys[0][1]),
                  fill=outline, width=125)
        draw.line((torso_cx + 185, torso_cy - 105, paw_xys[1][0], paw_xys[1][1]),
                  fill=outline, width=125)
        for px, py in paw_xys:
            draw.ellipse((px - 70, py - 70, px + 70, py + 70),
                         fill=fur, outline=outline, width=18)
    else:
        for px, py in paw_xys:
            draw.line((torso_cx + (-170 if px < torso_cx else 170), torso_cy - 120, px, py),
                      fill=outline, width=125)
            draw.ellipse((px - 74, py - 74, px + 74, py + 74), fill=fur, outline=outline, width=18)
    draw.line((torso_cx - 125, torso_cy + 320, left_foot[0], left_foot[1]), fill=outline, width=130)
    draw.line((torso_cx + 125, torso_cy + 320, right_foot[0], right_foot[1]), fill=outline, width=130)
    for fx, fy in (left_foot, right_foot):
        draw.ellipse((fx - 95, fy - 55, fx + 95, fy + 55), fill=fur, outline=outline, width=18)
    path = REACTIONS / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)
    alpha = canvas.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox or canvas.size != (1080, 1920):
        raise RuntimeError(f"Invalid native reaction: {name}")
    height_ratio = (bbox[3] - bbox[1]) / 1920
    if not 0.65 <= height_ratio <= 0.75:
        raise RuntimeError(f"{name} visible height {height_ratio:.3f} outside 65-75%")
    landmarks = {
        "left_eye": [head_cx - 105, eye_y], "right_eye": [head_cx + 105, eye_y],
        "mouth_center": [head_cx, mouth_y], "left_paw": list(paw_xys[0]),
        "right_paw": list(paw_xys[1]), "body_center": [torso_cx, torso_cy],
        "left_foot": list(left_foot), "right_foot": list(right_foot),
    }
    return {"id": name, "pose": pose, "path": rel(path), "sha256": sha256(path),
            "canvas": [1080, 1920], "occupied_bbox": list(bbox),
            "visible_height_ratio": round(height_ratio, 4), "landmarks": landmarks}


def build_reactions() -> dict[str, Any]:
    assets = [
        native_reaction("baseline_smug", "smug", 700, 1130),
        native_reaction("shielding_concern", "shield", 700, 1130),
        native_reaction("signature_read", "read", 430, 1130),
        native_reaction("signature_shock", "shock", 430, 1130),
        native_reaction("signature_recoil_one", "recoil_one", 430, 1130),
        native_reaction("signature_recoil_two", "recoil_two", 430, 1130),
        native_reaction("powered_read", "powered_read", 630, 1130),
        native_reaction("powered_eye_pop", "powered_eye_pop", 630, 1130),
        native_reaction("powered_recoil", "powered_recoil", 630, 1130),
    ]
    by_id = {item["id"]: item for item in assets}
    displacement = (by_id["signature_recoil_two"]["landmarks"]["body_center"][0]
                    - by_id["signature_shock"]["landmarks"]["body_center"][0])
    foot_drift = max(abs(by_id["signature_recoil_two"]["landmarks"][foot][0]
                         - by_id["signature_shock"]["landmarks"][foot][0])
                     for foot in ("left_foot", "right_foot"))
    if displacement < 90:
        raise RuntimeError("Signature body-center recoil is not measurable")
    if foot_drift > 1:
        raise RuntimeError("Signature feet are not a stable recoil reference")
    safe_regions: dict[str, tuple[int, int, int, int]] = {
        "signature_upper_inset": (55, 95, 1025, 400),
        "powered_display": (55, 95, 360, 720),
    }
    evidence_overlap_pixels: dict[str, int] = {}
    for asset_id, region_name in [
        *((asset_id, "signature_upper_inset") for asset_id in by_id if asset_id.startswith("signature_")),
        *((asset_id, "powered_display") for asset_id in by_id if asset_id.startswith("powered_")),
    ]:
        alpha = Image.open(ROOT / by_id[asset_id]["path"]).getchannel("A")
        occupied = sum(1 for pixel in alpha.crop(tuple(safe_regions[region_name])).getdata() if pixel)
        evidence_overlap_pixels[asset_id] = occupied
    if any(evidence_overlap_pixels.values()):
        raise RuntimeError(f"Reaction alpha overlaps evidence-safe region: {evidence_overlap_pixels}")
    overlay_windows = [
        ("baseline_smug", 8.0, 9.7), ("shielding_concern", 16.0, 18.3),
        ("signature_read", 29.5, 29.8), ("signature_shock", 29.8, 30.2),
        ("signature_recoil_one", 30.2, 30.6), ("signature_recoil_two", 30.6, 31.15),
        ("powered_read", 49.0, 49.55), ("powered_eye_pop", 49.55, 50.35),
        ("powered_recoil", 50.35, 52.6),
    ]
    transformed = [{"asset_id": asset, "window": [start, end], "overlay_xy": [0, 0],
                    "final_landmarks": by_id[asset]["landmarks"],
                    "final_occupied_bbox": by_id[asset]["occupied_bbox"]}
                   for asset, start, end in overlay_windows]
    manifest = {"schema_version": 2, "generation": "native_1080x1920_procedural_no_proxy_upscale",
                "generator_path": rel(Path(__file__).resolve()), "generator_sha256": sha256(Path(__file__).resolve()),
                "assets": assets, "signature_body_center_recoil_pixels": displacement,
                "signature_foot_reference_max_drift_pixels": foot_drift,
                "evidence_safe_regions": safe_regions,
                "evidence_safe_region_alpha_overlap_pixels": evidence_overlap_pixels,
                "final_overlay_geometry": transformed}
    REACTION_GATE.parent.mkdir(parents=True, exist_ok=True)
    REACTION_GATE.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def ass_time(seconds: float) -> str:
    cs = round(seconds * 100)
    hours, remainder = divmod(cs, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, hundredths = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{hundredths:02d}"


def ass_seconds(seconds: float) -> float:
    """Quantize once so the manifest and emitted ASS share exact intervals."""
    return round(seconds * 100) / 100


def caption_normalize(text: str) -> str:
    value = re.sub(r"['’]", "", text.lower())
    value = re.sub(r"\b1\s*,?\s*000\b", "one thousand", value)
    value = re.sub(r"\b300\b", "three hundred", value)
    value = re.sub(r"\b10\b", "ten", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def expand_numeric_caption_words(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand ASR numeral tokens to the lexical words used by the narration contract."""
    expanded: list[dict[str, Any]] = []
    replacements = {"300": ["Three", "hundred"], "1000": ["one", "thousand"], "10": ["Ten"]}
    for word in words:
        match = re.fullmatch(r"(\s*)(1,?000|300|10)([\s.,!?;:'\"…-]*)", str(word["word"]))
        if not match:
            expanded.append(dict(word))
            continue
        leading, numeral, suffix = match.groups()
        parts = replacements[numeral.replace(",", "")]
        start, end = float(word["start"]), float(word["end"])
        step = (end - start) / len(parts)
        for index, part in enumerate(parts):
            expanded.append({
                "word": (leading if index == 0 else " ") + part
                    + (suffix if index == len(parts) - 1 else ""),
                "start": start + step * index,
                "end": end if index == len(parts) - 1 else start + step * (index + 1),
            })
    return expanded


def write_captions(tts: dict[str, Any]) -> list[dict[str, Any]]:
    calibration = load(CALIBRATION)["ffmpeg_profile"]
    english = calibration["english"]
    base_size = int(english["base_font_size_px"])
    keyword_size = int(english["keyword_font_size_px"])
    outline = int(calibration["stroke_width_px"])
    margin_h = round(1080 * float(calibration["horizontal_margin_ratio"]))
    center_y = round(1920 * float(calibration["caption_center_y_ratio"]))
    margin_v = 1920 - center_y
    burst_min = int(calibration["burst_words_min"])
    burst_max = int(calibration["burst_words_max"])
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,Komika Axis,{base_size},&H00FFFFFF,&H0000D7FF,&H00201812,&H80000000,0,0,0,0,100,100,1,0,1,{outline},2,2,{margin_h},{margin_h},{margin_v},1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events, bursts, event_records = [], [], []
    for line in tts["lines"]:
        offset = float(line["envelope"][0])
        words = expand_numeric_caption_words(line["asr"]["words"])
        expected_word_count = len(re.findall(r"\S+", line["source_text"]))
        if len(words) != expected_word_count:
            raise RuntimeError(
                f"ASR word count differs from source text for {line['id']}: "
                f"asr={len(words)} source={expected_word_count}"
            )
        reconstructed = "".join(word["word"] for word in words).strip()
        if caption_normalize(reconstructed) != caption_normalize(line["source_text"]):
            raise RuntimeError(f"Expanded caption words differ from narration text: {line['id']}")
        fixed_partitions = {"hook": [4, 3, 4, 3], "cta": [4, 5]}
        if line["id"] in fixed_partitions:
            sizes = fixed_partitions[line["id"]]
            if sum(sizes) != len(words):
                raise RuntimeError(f"Fixed caption partition mismatch for {line['id']}")
            groups, cursor = [], 0
            for size in sizes:
                groups.append(words[cursor:cursor + size])
                cursor += size
        else:
            groups = [words[index:index + 4] for index in range(0, len(words), 4)]
        if len(groups) > 1 and len(groups[-1]) < burst_min:
            remainder = groups.pop()
            if len(groups[-1]) + len(remainder) > burst_max:
                raise RuntimeError(f"Cannot rebalance caption groups for {line['id']}")
            groups[-1].extend(remainder)
        for index, group in enumerate(groups):
            start = ass_seconds(offset + float(group[0]["start"]))
            natural_end = offset + float(group[-1]["end"]) + 0.08
            next_start = (offset + float(groups[index + 1][0]["start"])
                          if index + 1 < len(groups) else DURATION)
            end = ass_seconds(min(DURATION, natural_end, next_start))
            if end <= start:
                raise RuntimeError(f"Caption interval collapsed after ASS quantization: {line['id']}")
            tokens = re.findall(r"\S+", "".join(word["word"] for word in group).strip())
            emphasis = max(range(len(tokens)), key=lambda item: len(re.sub(r"\W", "", tokens[item])))
            keyword_scale = round(keyword_size / base_size * 100)
            text = " ".join((r"{\c&H00D7FF&\b1\t(0,140,\fscx"
                             + str(keyword_scale) + r"\fscy" + str(keyword_scale) + ")}"
                             + token + r"{\rCaption}")
                            if item == emphasis else token for item, token in enumerate(tokens))
            bursts.append({"line_id": line["id"], "start": start, "end": end,
                           "words": group, "word_count": len(tokens), "emphasis_index": emphasis})
            events.append(f"Dialogue: 5,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{text}")
            event_records.append({"line_id": line["id"], "start": start, "end": end})
    hook = next(item for item in bursts if item["line_id"] == "hook")
    hook_word = next(item for item in tts["lines"] if item["id"] == "hook")["asr"]["words"][0]
    if hook["start"] - float(hook_word["start"]) > 0.2:
        raise RuntimeError("Hook speech caption does not begin within 0.2s of first audible word")
    if any(not burst_min <= item["word_count"] <= burst_max for item in bursts):
        raise RuntimeError("Caption burst outside 2-5 words")
    burst_intervals = [{"line_id": item["line_id"], "start": item["start"], "end": item["end"]}
                       for item in bursts]
    if len(events) != len(bursts) or event_records != burst_intervals:
        raise RuntimeError("ASS caption events do not exactly match caption_bursts")
    for left, right in zip(bursts, bursts[1:]):
        if left["line_id"] == right["line_id"] and float(left["end"]) > float(right["start"]):
            raise RuntimeError(f"Overlapping ASS caption events in {left['line_id']}")
    ASS.parent.mkdir(parents=True, exist_ok=True)
    ASS.write_text(header + "\n".join(events) + "\n")
    return bursts


def focus_expression(points: list[tuple[float, float]], time_expression: str) -> str:
    """Piecewise-linear V9 focus evaluated in crop-local time."""
    expression = str(points[-1][1])
    for (at, focus), (next_at, next_focus) in reversed(list(zip(points, points[1:]))):
        slope = (next_focus - focus) / (next_at - at)
        value = f"({focus}+({slope})*(({time_expression})-{at}))"
        expression = f"if(lt({time_expression},{next_at}),{value},{expression})"
    return expression


def source_filter(
    record: dict[str, Any], offset: float, seconds: float, focus_override: float | None = None,
) -> tuple[str, str | None]:
    points = [(float(item["time_seconds"]), float(item["horizontal_focus_normalized"]))
              for item in record["focus_trajectory"]]
    focus = str(focus_override) if focus_override is not None \
        else focus_expression(points, f"(t+{offset})")
    return (f"scale=-2:1920,crop=1080:1920:"
            f"x='clip(({focus})*iw-540,0,iw-1080)':y=0,fps=30,"
            f"trim=duration={seconds},setpts=PTS-STARTPTS", focus)


def render_piece(
    name: str, record: dict[str, Any], offset: float, seconds: float,
    focus_override: float | None = None,
) -> Path:
    start, end = map(float, record["source_interval_local_seconds"])
    if offset < 0 or start + offset + seconds > end + 1e-6:
        raise RuntimeError(f"{name} exceeds approved V9 crop interval")
    destination = SEGMENTS / f"{name}.mkv"
    video_filter, _ = source_filter(record, offset, seconds, focus_override)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start + offset),
         "-t", str(seconds), "-i", str(ROOT / record["source_path"]), "-filter_complex",
         f"[0:v]{video_filter}[v]", "-map", "[v]", "-an",
         "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(destination)])
    return destination


def render_evidence_layout(
    name: str, record: dict[str, Any], offset: float, seconds: float,
    inset: tuple[int, int, int, int],
) -> Path:
    """Render a real-source inset over a subdued full-frame source backdrop."""
    start, end = map(float, record["source_interval_local_seconds"])
    if offset < 0 or start + offset + seconds > end + 1e-6:
        raise RuntimeError(f"{name} exceeds approved V9 crop interval")
    x, y, width, height = inset
    destination = SEGMENTS / f"{name}.mkv"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start + offset),
         "-t", str(seconds), "-i", str(ROOT / record["source_path"]), "-filter_complex",
         "[0:v]split=2[bg][proof];"
         "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
         "boxblur=24:2,eq=brightness=-0.22:saturation=0.55[back];"
         f"[proof]scale={width}:{height}:force_original_aspect_ratio=decrease,"
         f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black[inset];"
         f"[back][inset]overlay={x}:{y},fps=30,trim=duration={seconds},"
         "setpts=PTS-STARTPTS[v]",
         "-map", "[v]", "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p",
         str(destination)])
    return destination


def timed_audio(source: Path, start: float, total: float, destination: Path) -> Path:
    # Leading silence is samples, not PTS metadata.
    if abs(start) < 1e-9:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
             "-af", f"apad,atrim=0:{total}", "-ar", str(RATE), "-ac", "2",
             "-c:a", "pcm_s16le", str(destination)])
    else:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-t", str(start),
             "-i", f"anullsrc=r={RATE}:cl=stereo", "-i", str(source), "-filter_complex",
             f"[0:a][1:a]concat=n=2:v=0:a=1,apad,atrim=0:{total}[a]", "-map", "[a]",
             "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(destination)])
    return destination


def make_procedural_audio_assets(
    total_duration: float = DURATION,
    asset_ids: set[str] | None = None,
    output_dir: Path = AUDIO_ASSETS,
) -> tuple[list[dict[str, Any]], list[tuple[Path, float]]]:
    """Create an original low bed and short event sounds as native PCM."""
    output_dir.mkdir(parents=True, exist_ok=True)
    definitions = [
        ("hook_whoosh", 0.00, 0.32, 720, 1320),
        ("drop", 1.45, 0.28, 510, 250),
        ("impact", 2.18, 0.22, 105, 58),
        ("split", 0.76, 0.25, 880, 1480),
        ("signature_recoil", 30.18, 0.32, 430, 180),
        ("cta_like", 38.20, 0.16, 820, 1040),
        ("cta_subscribe", 39.00, 0.18, 920, 1180),
        ("cta_comment", 40.20, 0.20, 1020, 1320),
        ("powered", 49.00, 0.34, 330, 990),
        ("powered_eye_pop", 49.55, 0.16, 1250, 1780),
        ("powered_recoil", 50.35, 0.30, 390, 170),
        ("mechanism_card", 42.00, 0.22, 600, 900),
        ("mechanism_scale_one", 44.20, 0.18, 680, 1020),
        ("mechanism_scale_two", 46.40, 0.18, 760, 1140),
        ("loop", 56.00, 0.28, 520, 920),
    ]
    records: list[dict[str, Any]] = []
    placements: list[tuple[Path, float]] = []
    bed = output_dir / "procedural_continuous_bed.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-t", str(total_duration),
         "-i", "sine=frequency=196:sample_rate=48000", "-f", "lavfi", "-t", str(total_duration),
         "-i", "sine=frequency=294:sample_rate=48000", "-f", "lavfi", "-t", str(total_duration),
         "-i", "sine=frequency=392:sample_rate=48000", "-filter_complex",
         "[0:a]volume=0.120[a0];[1:a]volume=0.070[a1];[2:a]volume=0.044[a2];"
         "[a0][a1][a2]amix=inputs=3:normalize=0,tremolo=f=0.12:d=0.18,"
         "highpass=f=150,lowpass=f=1800,"
         f"afade=t=in:st=0:d=0.4,afade=t=out:st={total_duration - 0.5}:d=0.5[a]",
         "-map", "[a]", "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(bed)])
    records.append({"id": "procedural_continuous_bed", "path": rel(bed), "sha256": sha256(bed),
                    "provenance": "original_procedural_phone_band_harmonic_pad_no_external_asset",
                    "generator": "ffmpeg lavfi 196_294_392hz_harmonic_pad",
                    "phone_translation_band_hz": [150, 2000],
                    "window": [0.0, total_duration]})
    placements.append((bed, 0.0))
    for asset_id, at, seconds, start_hz, end_hz in definitions:
        if asset_ids is not None and asset_id not in asset_ids:
            continue
        path = output_dir / f"{asset_id}.wav"
        expression = f"{start_hz}+({end_hz}-{start_hz})*t/{seconds}"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-t", str(seconds),
             "-i", f"aevalsrc=0.22*sin(2*PI*({expression})*t):s={RATE}:c=stereo",
             "-af", f"afade=t=in:st=0:d=0.02,afade=t=out:st={max(0.03, seconds - 0.12)}:d=0.12,"
                    "acompressor=threshold=0.1:ratio=4:attack=5:release=80:makeup=1,"
                    "loudnorm=I=-22:TP=-3:LRA=8",
             "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(path)])
        records.append({"id": asset_id, "path": rel(path), "sha256": sha256(path),
                        "provenance": "original_procedural_event_sfx_generated_locally_no_external_asset",
                        "generator": "ffmpeg lavfi aevalsrc frequency sweep", "window": [at, at + seconds]})
        placements.append((path, at))
    return records, placements


def render_mechanism_piece(
    concrete: dict[str, Any], dirt: dict[str, Any], destination: Path
) -> dict[str, Any]:
    """Build real locked-frame concrete/red-dirt evidence with two scale changes."""
    concrete_offset = 4.8
    dirt_offset = 0.4
    concrete_at = float(concrete["source_interval_local_seconds"][0]) + concrete_offset
    dirt_at = float(dirt["source_interval_local_seconds"][0]) + dirt_offset
    concrete_source, dirt_source = ROOT / concrete["source_path"], ROOT / dirt["source_path"]
    concrete_focus = 0.5
    dirt_focus = 0.1
    concrete_frame = SEGMENTS / "mechanism_concrete_locked.png"
    dirt_frame = SEGMENTS / "mechanism_red_dirt_locked.png"
    for source, at, frame in ((concrete_source, concrete_at, concrete_frame),
                              (dirt_source, dirt_at, dirt_frame)):
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(at),
             "-i", str(source), "-frames:v", "1", "-update", "1", str(frame)])
    # Three consecutive native 1080x1920 layouts create two actual scale changes.
    scale_states = [(0.0, 2.2, 1.04), (2.2, 4.4, 1.16), (4.4, 7.0, 1.28)]
    state_paths = []
    motion_states: list[dict[str, Any]] = []
    for index, (start, end, scale) in enumerate(scale_states):
        state = SEGMENTS / f"mechanism_scale_{index}.mkv"
        state_duration = end - start
        width = round(round(1080 * scale) / 2) * 2
        height = round(round(960 * scale) / 2) * 2
        progress = f"t/{state_duration}"
        scaled_concrete = SEGMENTS / f"mechanism_concrete_scaled_{index}.png"
        scaled_dirt = SEGMENTS / f"mechanism_red_dirt_scaled_{index}.png"
        for source_frame, scaled_frame in (
            (concrete_frame, scaled_concrete), (dirt_frame, scaled_dirt)
        ):
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-i", str(source_frame), "-vf",
                 f"scale={width}:{height}:force_original_aspect_ratio=increase",
                 "-frames:v", "1", "-update", "1", str(scaled_frame)])
        with Image.open(scaled_concrete) as image:
            concrete_width, concrete_height = image.size
        with Image.open(scaled_dirt) as image:
            dirt_width, dirt_height = image.size

        def clipped(value: float, maximum: float) -> float:
            return max(0.0, min(value, maximum))

        concrete_x_start = clipped(concrete_focus * concrete_width - 540, concrete_width - 1080)
        concrete_y_start = clipped((concrete_height - 960) / 2, concrete_height - 960)
        dirt_x_start = 0.0
        dirt_y_start = clipped((dirt_height - 960) / 2, dirt_height - 960)
        effective_concrete = [
            round(clipped(concrete_focus * concrete_width - 540 + 45, concrete_width - 1080)
                  - concrete_x_start),
            round(clipped((concrete_height - 960) / 2 + 18, concrete_height - 960)
                  - concrete_y_start),
        ]
        effective_dirt = [
            round(clipped(60, dirt_width - 1080) - dirt_x_start),
            round(clipped((dirt_height - 960) / 2 + 18, dirt_height - 960)
                  - dirt_y_start),
        ]
        if effective_concrete != [45, 18] or effective_dirt != [60, 18]:
            raise RuntimeError(
                f"Mechanism state {index} clipped required evidence pan: "
                f"concrete={effective_concrete}, red_dirt={effective_dirt}"
            )
        motion_states.append({
            "window": [start + 42.0, end + 42.0], "scale": scale,
            "concrete_scaled_canvas": [concrete_width, concrete_height],
            "red_dirt_scaled_canvas": [dirt_width, dirt_height],
            "concrete_effective_delta_pixels": effective_concrete,
            "red_dirt_effective_delta_pixels": effective_dirt,
        })
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-loop", "1", "-framerate", "30", "-t", str(state_duration),
             "-i", str(scaled_concrete),
             "-loop", "1", "-framerate", "30", "-t", str(state_duration),
             "-i", str(scaled_dirt),
             "-filter_complex",
             f"[0:v]crop=1080:960:x='clip({concrete_focus}*iw-540+45*({progress}),0,iw-1080)':"
             f"y='clip((ih-960)/2+18*({progress}),0,ih-960)',"
             "setpts=PTS-STARTPTS[c];"
             f"[1:v]crop=1080:960:x='60*({progress})':"
             f"y='clip((ih-960)/2+18*({progress}),0,ih-960)',"
             "setpts=PTS-STARTPTS[d];"
             "[c][d]vstack=inputs=2,"
             f"drawbox=x='45+8*sin(t*5)':y='1260+8*cos(t*5)':w=470:h=630:"
             "color=0x00D7FF@0.9:t=8,"
             "drawbox=x=820:y=1260:w=10:h=420:color=white@0.9:t=fill,"
             "drawbox=x=780:y=1260:w=90:h=10:color=white@0.9:t=fill,"
             "drawbox=x=780:y=1670:w=90:h=10:color=white@0.9:t=fill,"
             f"fps=30,trim=duration={state_duration},setpts=PTS-STARTPTS[v]",
             "-map", "[v]", "-an", "-t", str(state_duration),
             "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(state)])
        state_paths.append(state)
    concat = SEGMENTS / "mechanism_scale_concat.txt"
    concat.write_text("".join(f"file '{path.resolve()}'\n" for path in state_paths))
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-t", "7", "-c", "copy", str(destination)])
    return {
        "layout": "locked_real_concrete_frame_over_locked_real_red_dirt_frame",
        "concrete_source": rel(concrete_source), "concrete_frame_seconds": concrete_at,
        "red_dirt_source": rel(dirt_source), "red_dirt_frame_seconds": dirt_at,
        "frame_contract": "different_tests_possible_mechanism_not_controlled_impact_proof",
        "concrete_focus_normalized": concrete_focus,
        "red_dirt_focus_normalized": dirt_focus,
        "moving_tracker": {"region": "phone_held_over_red_dirt_test_environment",
                           "box": [45, 1260, 515, 1890],
                           "motion": "8px sinusoidal pulse"},
        "continuous_camera_motion": {
            "mode": "one_way_evidence_pan",
            "requested_concrete_delta_pixels": [45, 18],
            "requested_red_dirt_delta_pixels": [60, 18],
            "reset_only_at_information_scale_change": True,
            "states": motion_states,
        },
        "stopping_distance_annotation": [780, 1260, 870, 1680],
        "scale_states": [{"window": [start + 42.0, end + 42.0], "scale": scale}
                         for start, end, scale in scale_states],
    }


def main() -> None:
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Missing executable: {executable}")
    storyboard, source_manifest, tts, implementation_review = validate_inputs()
    reaction_manifest = build_reactions()
    bursts = write_captions(tts)
    records = {record["id"]: record for record in source_manifest["crop_previews"]}
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    focus_overrides = {"hook_host": 0.44}
    schedule = [
        ("hook_host", "thousand_action", 0.0, 0.75), ("hook_split", "three_hundred_result", 0.0, 0.70),
        ("hook_scale", "thousand_action", 9.2, 0.80), ("hook_powered", "thousand_result", 4.2, 0.75),
        ("waist_a", "waist_action", 0.0, 5.0), ("waist_b", "waist_result", 0.0, 2.0),
        ("ten_a", "ten_stories_action", 0.0, 6.0), ("ten_b", "ten_stories_result", 0.0, 3.0),
        ("rigid", "ten_stories_result", 1.0, 3.0),
        ("three_a", "three_hundred_action", 0.0, 5.0), ("three_b", "three_hundred_result", 0.0, 2.5),
        ("signature", "three_hundred_result", 0.0, 4.0),
        ("thousand_setup", "thousand_action", 0.0, 4.5),
        ("cta_real", "thousand_action", 6.0, 2.0),
        ("powered", "thousand_result", 0.0, 3.6), ("quote", "thousand_result", 3.1, 3.3),
        ("quote_tail", "thousand_result", 5.8, 0.1),
        ("loop", "thousand_result", 4.5, 2.0),
    ]
    pieces = {name: render_piece(name, records[record_id], offset, seconds,
                                 focus_overrides.get(name))
              for name, record_id, offset, seconds in schedule}
    pieces["signature"] = render_evidence_layout(
        "signature", records["three_hundred_result"], 0.0, 4.0, (55, 95, 970, 304))
    pieces["powered"] = render_evidence_layout(
        "powered", records["thousand_result"], 0.0, 3.6, (55, 95, 304, 624))
    mechanism = SEGMENTS / "mechanism.mkv"
    mechanism_evidence = render_mechanism_piece(records["waist_action"], records["thousand_result"], mechanism)
    pieces["mechanism"] = mechanism
    pexels_piece = SEGMENTS / "cta_illustration.mkv"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-t", "2", "-i", str(PEXELS),
         "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,"
                "drawbox=x=30:y=30:w=410:h=105:color=black@0.75:t=fill,"
                "drawtext=fontfile=assets/fonts/Komika-Axis.ttf:text=ILLUSTRATION:"
                "x=55:y=52:fontsize=55:fontcolor=white",
         "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(pexels_piece)])
    ordered = ["hook_host", "hook_split", "hook_scale", "hook_powered", "waist_a", "waist_b",
               "ten_a", "ten_b", "rigid", "three_a", "three_b", "signature",
               "thousand_setup", "cta_illustration", "cta_real", "mechanism",
               "powered", "quote", "quote_tail", "loop"]
    duration_by_name = {name: seconds for name, _, _, seconds in schedule}
    duration_by_name.update({"cta_illustration": 2.0, "mechanism": 7.0})
    source_by_name = {name: pexels_piece if name == "cta_illustration" else pieces[name]
                      for name in ordered}
    visual = WORK / "visual_unadorned.nut"
    concat_command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for name in ordered:
        concat_command += ["-i", str(source_by_name[name])]
    concat_filters = []
    cumulative_seconds = 0.0
    previous_end_frame = 0
    frame_plan = []
    for index, name in enumerate(ordered):
        cumulative_seconds += duration_by_name[name]
        end_frame = math.floor(cumulative_seconds * FPS + 0.5)
        frame_count = end_frame - previous_end_frame
        if frame_count <= 0:
            raise RuntimeError(f"Non-positive visual frame allocation: {name}")
        concat_filters.append(
            f"[{index}:v]fps={FPS},tpad=stop_mode=clone:stop_duration=0.12,"
            f"trim=start_frame=0:end_frame={frame_count},setpts=N/({FPS}*TB)[v{index}]"
        )
        frame_plan.append({"name": name, "frames": frame_count,
                           "start_frame": previous_end_frame, "end_frame": end_frame})
        previous_end_frame = end_frame
    if previous_end_frame != round(DURATION * FPS):
        raise RuntimeError(f"Visual frame plan is {previous_end_frame}, expected {round(DURATION * FPS)}")
    concat_filters.append(
        "".join(f"[v{index}]" for index in range(len(ordered)))
        + f"concat=n={len(ordered)}:v=1:a=0,fps={FPS},"
          f"trim=start_frame=0:end_frame={round(DURATION * FPS)},"
          f"setpts=N/({FPS}*TB)[visual]"
    )
    concat_command += ["-filter_complex", ";".join(concat_filters), "-map", "[visual]",
                       "-frames:v", str(round(DURATION * FPS)), "-an", "-c:v", "ffv1",
                       "-level", "3", "-pix_fmt", "yuv420p", str(visual)]
    run(concat_command)
    # Overlay native poses only in short, distinct proof-following windows.
    overlays = [(item["asset_id"], *item["window"], 0, 0)
                for item in reaction_manifest["final_overlay_geometry"]]
    asset_map = {item["id"]: ROOT / item["path"] for item in reaction_manifest["assets"]}
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(visual)]
    for asset, *_ in overlays:
        command += ["-loop", "1", "-t", str(DURATION), "-i", str(asset_map[asset])]
    filters = ["[0:v]drawbox=x=55:y=95:w=970:h=305:color=0x00D7FF@0.9:t=8:"
               "enable='between(t,29.5,33.5)',"
               "drawbox=x=55:y=95:w=305:h=625:color=0x00D7FF@0.9:t=8:"
               "enable='between(t,49,52.6)'[layout]"]
    current = "layout"
    for index, (asset, start, end, x, y) in enumerate(overlays, 1):
        output = f"r{index}"
        filters.append(f"[{current}][{index}:v]overlay={x}:{y}:enable='between(t,{start},{end})'[{output}]")
        current = output
    filters.append(f"[{current}]ass='{ASS.as_posix()}'[v]")
    command += ["-filter_complex", ";".join(filters), "-map", "[v]", "-an", "-t", str(DURATION),
                "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-r", str(FPS), "-vsync", "cfr", str(WORK / "visual_master.mp4")]
    run(command)
    TRACKS.mkdir(parents=True, exist_ok=True)
    tracks = []
    for index, line in enumerate(tts["lines"]):
        track = TRACKS / f"{index:02d}_{line['id']}.wav"
        tracks.append(timed_audio(ROOT / line["path"], float(line["envelope"][0]), DURATION, track))
    # Preserve only the exact approved quote; every visual source occurrence is otherwise -an.
    quote = TRACKS / "source_quote.wav"
    source = ROOT / records["thousand_result"]["source_path"]
    quote_clip = TRACKS / "source_quote_clip.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "490.6", "-t", "3.3",
         "-i", str(source), "-vn", "-af", "afade=t=in:st=0:d=0.12,afade=t=out:st=3.1:d=0.2,"
         "loudnorm=I=-18:TP=-2:LRA=8", "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(quote_clip)])
    tracks.append(timed_audio(quote_clip, 52.6, DURATION, quote))
    audio_assets, audio_placements = make_procedural_audio_assets()
    required_sfx = set(storyboard["audio_contract"]["required_asset_ids"])
    generated_sfx = {asset["id"] for asset in audio_assets
                     if asset["id"] != "procedural_continuous_bed"}
    if generated_sfx != required_sfx:
        raise RuntimeError(
            f"Procedural SFX set differs from storyboard: generated={sorted(generated_sfx)} "
            f"required={sorted(required_sfx)}"
        )
    for index, (asset, start) in enumerate(audio_placements):
        track = TRACKS / f"production_{index:02d}_{asset.stem}.wav"
        tracks.append(timed_audio(asset, start, DURATION, track))
    mix_command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for track in tracks:
        mix_command += ["-i", str(track)]
    mix_command += ["-filter_complex", "".join(f"[{i}:a]" for i in range(len(tracks))) +
                    f"amix=inputs={len(tracks)}:normalize=0,"
                    "loudnorm=I=-16:TP=-1.5:LRA=8[a]", "-map", "[a]", "-t", str(DURATION),
                    "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(WORK / "audio_master.wav")]
    run(mix_command)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(WORK / "visual_master.mp4"),
         "-i", str(WORK / "audio_master.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-ar", str(RATE), "-ac", "2", "-t", str(DURATION),
         "-movflags", "+faststart", str(BASE)])
    occurrences = [{"name": name, "crop_id": crop, "kind": "youtube",
                    "final_duration": seconds, "source_offset": offset,
                    "focus_override": focus_overrides.get(name)}
                   for name, crop, offset, seconds in schedule]
    occurrences.extend([
        {"name": "mechanism_concrete_locked_frame", "crop_id": "waist_action", "kind": "youtube",
         "final_duration": 7.0, "source_offset": 4.8},
        {"name": "mechanism_red_dirt_locked_frame", "crop_id": "thousand_result", "kind": "youtube",
         "final_duration": 7.0, "source_offset": 0.4},
    ])
    crop_youtube = {record["id"]: record["youtube_id"] for record in source_manifest["crop_previews"]}
    aggregate: dict[str, float] = {}
    for item in occurrences:
        youtube_id = crop_youtube[item["crop_id"]]
        item["youtube_id"] = youtube_id
        aggregate[youtube_id] = round(aggregate.get(youtube_id, 0.0) + float(item["final_duration"]), 4)
    source_usage = {"schema_version": 1, "source_manifest_path": rel(SOURCE_MANIFEST),
                    "source_manifest_sha256": sha256(SOURCE_MANIFEST), "occurrences": occurrences,
                    "aggregate_youtube_usage_seconds": aggregate,
                    "all_visual_source_audio_muted": True,
                    "only_approved_quote": {"window": [52.6, 55.9], "text": "It is on! That's unreal!"}}
    SOURCE_USAGE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_USAGE.write_text(json.dumps(source_usage, indent=2) + "\n")
    applied_focus = []
    for name, crop, offset, seconds in schedule:
        record = records[crop]
        override = focus_overrides.get(name)
        _, expression = source_filter(record, offset, seconds, override)
        applied_focus.append({"occurrence": name, "crop_id": crop, "source_offset": offset,
                              "duration": seconds, "focus_trajectory": record["focus_trajectory"],
                              "focus_override": override,
                              "applied_focus_expression": expression})
    manifest = {"schema_version": 3, "status": "BASE_RENDERED", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "artifact": rel(BASE), "artifact_sha256": sha256(BASE),
                "renderer_path": rel(Path(__file__).resolve()), "renderer_sha256": sha256(Path(__file__).resolve()),
                "storyboard_sha256": sha256(STORYBOARD), "tts_manifest_sha256": sha256(TTS_MANIFEST),
                "tts_generator_sha256": sha256(TTS_GENERATOR), "profile_sha256": sha256(PROFILE),
                "source_manifest_sha256": sha256(SOURCE_MANIFEST), "source_usage_sha256": sha256(SOURCE_USAGE),
                "pexels_license_sha256": sha256(PEXELS_LICENSE), "pexels_asset_sha256": sha256(PEXELS),
                "font_sha256": sha256(FONT), "caption_calibration_sha256": sha256(CALIBRATION),
                "reaction_gate_path": rel(REACTION_GATE), "reaction_gate_sha256": sha256(REACTION_GATE),
                "caption_bursts": bursts, "source_audio_policy": "muted_except_exact_quote",
                "caption_profile_applied": load(CALIBRATION)["ffmpeg_profile"],
                "visual_frame_plan": frame_plan,
                "applied_focus_trajectories": applied_focus,
                "mechanism_evidence": mechanism_evidence,
                "audio_assets": audio_assets,
                "audio_track_duration_seconds": DURATION,
                "timed_audio_policy": "real_pcm_leading_silence_start_zero_uses_direct_apad",
                "implementation_review_path": rel(IMPLEMENTATION_REVIEW),
                "implementation_review_sha256": sha256(IMPLEMENTATION_REVIEW),
                "implementation_review_status": implementation_review["status"]}
    RENDER_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"PASS base: {BASE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
