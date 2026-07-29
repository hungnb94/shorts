#!/usr/bin/env python3
"""Render Capytech V7: a deterministic 3D charging-time test.

Run normally to build the Blender visual, synthesize original audio, and mux the
1080x1920 exact-final MP4. Blender invokes this same file with
``--blender-stage`` for scene creation/rendering.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v7_charge_test_storyboard.json"
WORK = ROOT / "output/projects/capytech/clips/capytech_v7_charge_test_work"
FINAL = ROOT / "output/projects/capytech/final/2026-07-29-capytech_v7_charge_test.mp4"
VISUAL = WORK / "visual_540x960.mp4"
PROGRESSION_VISUAL = WORK / "visual_progression_540x960.mp4"
AUDIO_RAW = WORK / "audio_raw.wav"
AUDIO_NORM = WORK / "audio_normalized.wav"
BLEND_FILE = WORK / "capytech_v7_charge_test.blend"
PREVIEW_DIR = WORK / "previews"
FRAMES_DIR = WORK / "frames"
FPS = 30
DURATION = 52.0
FRAMES = int(FPS * DURATION)


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def validate_storyboard() -> dict:
    data = json.loads(STORYBOARD.read_text())
    assert data["duration_seconds"] == DURATION
    assert data["fps"] == FPS
    beats = data["beats"]
    assert beats[0]["start"] == 0.0
    assert beats[-1]["end"] == DURATION
    for left, right in zip(beats, beats[1:]):
        assert left["end"] == right["start"], (left["id"], right["id"])
    fmt = data["format"]
    assert len({fmt["central_object"]}) == 1
    assert len({fmt["repeated_action"]}) == 1
    assert len({fmt["changing_scalar"]}) == 1
    return data


def parse_loudnorm_json(stderr: str) -> dict:
    start = stderr.rfind("{")
    end = stderr.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("loudnorm did not emit JSON")
    return json.loads(stderr[start : end + 1])


def synth_audio(storyboard: dict) -> None:
    import numpy as np

    sr = 48_000
    n = int(DURATION * sr)
    t = np.arange(n, dtype=np.float64) / sr
    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(707)

    def add(signal: np.ndarray, start: float, pan: float = 0.0, gain: float = 1.0) -> None:
        idx = int(start * sr)
        if idx >= n:
            return
        signal = signal[: n - idx] * gain
        l_gain = math.cos((pan + 1.0) * math.pi / 4.0)
        r_gain = math.sin((pan + 1.0) * math.pi / 4.0)
        left[idx : idx + len(signal)] += signal * l_gain
        right[idx : idx + len(signal)] += signal * r_gain

    def env(length: int, attack: float = 0.01, release: float = 0.12) -> np.ndarray:
        e = np.ones(length, dtype=np.float64)
        a = min(length, max(1, int(attack * sr)))
        r = min(length, max(1, int(release * sr)))
        e[:a] = np.linspace(0.0, 1.0, a)
        e[-r:] *= np.linspace(1.0, 0.0, r)
        return e

    def tone(freq: float, dur: float, kind: str = "sine", slide: float = 0.0) -> np.ndarray:
        count = max(1, int(dur * sr))
        tt = np.arange(count, dtype=np.float64) / sr
        phase = 2 * np.pi * (freq * tt + 0.5 * slide * tt * tt)
        if kind == "square":
            sig = np.sign(np.sin(phase))
        elif kind == "saw":
            sig = 2.0 * ((freq * tt + 0.5 * slide * tt * tt) % 1.0) - 1.0
        else:
            sig = np.sin(phase)
        return sig * env(count, 0.008, min(0.16, dur * 0.45))

    def noise(dur: float, color: float = 0.0) -> np.ndarray:
        count = max(1, int(dur * sr))
        sig = rng.normal(0, 1, count)
        if color > 0:
            # One-pole smoothing for softer, physical noise.
            alpha = min(0.98, color)
            for i in range(1, count):
                sig[i] = alpha * sig[i - 1] + (1 - alpha) * sig[i]
        peak = np.max(np.abs(sig)) or 1.0
        return sig / peak * env(count, 0.003, min(0.18, dur * 0.5))

    # Original playful score: a single theme gains harmonic weight each round.
    bpm = 120
    beat = 60 / bpm
    chord_roots = [110.0, 130.81, 146.83, 98.0]
    for b, start in enumerate(np.arange(0, DURATION, beat)):
        stage = 0 if start < 8.5 else 1 if start < 19.0 else 2 if start < 31.5 else 3
        root = chord_roots[(b // 8) % len(chord_roots)]
        pulse = tone(root, 0.22, "sine") + 0.22 * tone(root * 2, 0.22, "square")
        add(pulse, float(start), pan=-0.08 if b % 2 == 0 else 0.08, gain=0.075 + 0.012 * stage)
        if b % 2 == 0:
            pluck = tone(root * (2.0 + (b % 4) * 0.25), 0.12, "sine")
            add(pluck, float(start + 0.25), pan=0.28, gain=0.05 + 0.01 * stage)
        if stage >= 2 and b % 4 == 2:
            add(tone(root * 4, 0.09, "square"), float(start + 0.38), pan=-0.35, gain=0.025)

    # Soft four-on-the-floor tick; no external samples or licensing dependency.
    for start in np.arange(0, DURATION, beat):
        add(tone(60, 0.09, "sine", slide=-180), float(start), gain=0.10)
        add(noise(0.045, 0.35), float(start + beat / 2), pan=0.2, gain=0.025)

    def sfx(name: str, at: float) -> None:
        if name == "battery_alarm":
            for off in (0.0, 0.13):
                add(tone(880, 0.10, "square"), at + off, gain=0.12)
        elif name == "cable_whoosh":
            add(noise(0.26, 0.55), at, pan=-0.25, gain=0.13)
            add(tone(240, 0.22, "sine", slide=700), at, gain=0.08)
        elif name == "plug":
            add(tone(170, 0.08, "sine", slide=-450), at, gain=0.16)
            add(tone(1100, 0.07, "sine"), at + 0.055, gain=0.09)
        elif name in {"tiny_charge", "charge_tick"}:
            add(tone(620 if name == "tiny_charge" else 760, 0.12, "sine", slide=380), at, pan=0.25, gain=0.10)
        elif name == "fail_tick":
            add(tone(250, 0.24, "sine", slide=-500), at, gain=0.12)
        elif name == "stage_swipe":
            add(noise(0.30, 0.65), at, pan=-0.55, gain=0.10)
            add(tone(300, 0.26, "sine", slide=950), at, pan=0.3, gain=0.08)
        elif name in {"result_ding", "hope_chime", "full_charge"}:
            base = 660 if name == "result_ding" else 740 if name == "hope_chime" else 880
            for i, ratio in enumerate((1.0, 1.25, 1.5)):
                add(tone(base * ratio, 0.20, "sine"), at + 0.08 * i, pan=-0.2 + 0.2 * i, gain=0.09)
        elif name == "steam":
            add(noise(1.3, 0.85), at, pan=0.35, gain=0.11)
        elif name == "warning":
            for off in (0.0, 0.22):
                add(tone(420, 0.15, "square"), at + off, gain=0.09)
        elif name == "rapid_charge":
            add(tone(180, 1.3, "saw", slide=520), at, gain=0.08)
            add(noise(1.2, 0.76), at, gain=0.055)
        elif name == "cta_pop":
            add(tone(760, 0.11, "sine", slide=900), at, pan=0.45, gain=0.10)
        elif name == "swell":
            add(tone(75, 2.2, "sine", slide=70), at, gain=0.14)
            add(noise(1.6, 0.90), at + 0.4, gain=0.06)
        elif name == "strain":
            add(tone(95, 1.0, "saw", slide=-25), at, gain=0.09)
        elif name == "lift":
            add(tone(220, 1.2, "sine", slide=560), at, pan=0.1, gain=0.13)
        elif name == "pop":
            add(noise(0.45, 0.15), at, gain=0.35)
            add(tone(65, 0.50, "sine", slide=-70), at, gain=0.22)
            add(tone(1500, 0.18, "square"), at, gain=0.10)
        elif name == "fall":
            add(tone(75, 0.35, "sine", slide=-120), at, pan=-0.2, gain=0.20)
            add(noise(0.22, 0.4), at + 0.18, gain=0.14)
        elif name == "reset":
            add(tone(500, 0.36, "sine", slide=850), at, gain=0.11)

    for event in storyboard["sfx"]:
        sfx(event["event"], float(event["at"]))

    # Gentle side-chain-like dip around large SFX keeps their meaning readable.
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-9)
    stereo = np.stack([left / peak * 0.86, right / peak * 0.86], axis=1)
    pcm = np.clip(stereo * 32767, -32768, 32767).astype("<i2")
    with wave.open(str(AUDIO_RAW), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(pcm.tobytes())

    measure = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(AUDIO_RAW),
            "-af", "loudnorm=I=-16:TP=-2.3:LRA=8:print_format=json",
            "-f", "null", "-",
        ],
        capture=True,
    )
    stats = parse_loudnorm_json(measure.stderr)
    filt = (
        "loudnorm=I=-16:TP=-2.3:LRA=8:linear=true:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:print_format=summary,"
        "alimiter=limit=0.76:level=false"
    )
    run(["ffmpeg", "-y", "-i", str(AUDIO_RAW), "-af", filt, "-ar", "48000", "-ac", "2", str(AUDIO_NORM)])


def composite_progression() -> None:
    """Composite semantic progress after the base 3D render."""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    capture = cv2.VideoCapture(str(VISUAL))
    if not capture.isOpened():
        raise RuntimeError(f"Cannot open visual master: {VISUAL}")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if (width, height, frame_count) != (540, 960, FRAMES):
        raise RuntimeError(f"Unexpected visual shape: {(width, height, frame_count)}")
    fourcc = getattr(cv2, "VideoWriter_fourcc")(*"mp4v")
    writer = cv2.VideoWriter(str(PROGRESSION_VISUAL), fourcc, FPS, (width, height))
    if not writer.isOpened():
        raise RuntimeError("Cannot open progression video writer")

    font_path = ROOT / "assets/fonts/Komika-Axis.ttf"
    font_cache = {}

    def selected_font(size: int):
        if size not in font_cache:
            font_cache[size] = ImageFont.truetype(str(font_path), size)
        return font_cache[size]

    stage_windows = [
        (0.0, 8.5, 86), (8.5, 19.0, 209), (19.0, 31.5, 331),
        (31.5, 49.8, 454), (49.8, 52.0, 86),
    ]
    charge_windows = [
        (0.85, 7.8), (9.45, 18.3), (20.0, 30.8),
        (32.55, 42.0), (50.65, 52.0),
    ]
    result_events = [
        (5.50, 7.20, "+1%", (255, 92, 92)),
        (16.30, 18.00, "+14%", (255, 210, 54)),
        (26.30, 29.00, "FULL!", (62, 255, 126)),
    ]

    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        time = index / FPS

        # Elapsed-time rail: continuous information, not decorative motion.
        for start, end, center_x in stage_windows:
            if start <= time < end:
                progress = max(0.0, min(1.0, (time - start) / max(0.001, end - start)))
                left = center_x - 40
                cv2.rectangle(frame, (left, 131), (left + 80, 136), (35, 48, 63), -1, cv2.LINE_AA)
                cv2.rectangle(
                    frame,
                    (left, 131),
                    (left + max(2, round(80 * progress)), 136),
                    (255, 235, 40),
                    -1,
                    cv2.LINE_AA,
                )
                break

        # A physical energy pulse proves that the cable is actively charging.
        for start, end in charge_windows:
            if start <= time <= end:
                phase = ((time - start) % 0.72) / 0.72
                x = round(8 + 342 * phase)
                # Measured from the exact Blender frame: the cable runs from
                # roughly y=650 at frame-left to y=690 at the inserted port.
                y = round(650 + 40 * phase + 9 * math.sin(math.pi * phase))
                cv2.circle(frame, (x, y), 13, (255, 210, 45), -1, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 7, (255, 255, 245), -1, cv2.LINE_AA)
                break

        # Result bursts expose the same scalar without adding a second rule.
        for start, end, label, rgb in result_events:
            if start <= time <= end:
                local = (time - start) / max(0.001, end - start)
                size = round(40 * (1.0 + 0.08 * math.sin(local * math.pi * 5)))
                pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(pil)
                center = (390, 333)
                for ray in range(10):
                    angle = ray * math.tau / 10 + local * 0.35
                    r0, r1 = 52, 68 + 5 * math.sin(local * math.pi)
                    p0 = (center[0] + math.cos(angle) * r0, center[1] + math.sin(angle) * r0)
                    p1 = (center[0] + math.cos(angle) * r1, center[1] + math.sin(angle) * r1)
                    draw.line((p0, p1), fill=rgb, width=4)
                current_font = selected_font(size)
                box = draw.textbbox((0, 0), label, font=current_font, stroke_width=5)
                tx = center[0] - (box[2] - box[0]) / 2
                ty = center[1] - (box[3] - box[1]) / 2 - 4
                draw.text(
                    (tx, ty), label, font=current_font, fill=rgb,
                    stroke_width=6, stroke_fill=(8, 12, 25),
                )
                frame = cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
                break

        writer.write(frame)
        index += 1

    capture.release()
    writer.release()
    if index != FRAMES or not PROGRESSION_VISUAL.exists() or PROGRESSION_VISUAL.stat().st_size < 1_000_000:
        raise RuntimeError(f"Progression composite failed closed: {index}/{FRAMES} frames")


def mux_final() -> None:
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    visual_input = PROGRESSION_VISUAL if PROGRESSION_VISUAL.exists() else VISUAL
    run(
        [
            "ffmpeg", "-y", "-i", str(visual_input), "-i", str(AUDIO_NORM),
            "-filter_complex", "[0:v]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p[v]",
            "-map", "[v]", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
            "-r", "30", "-fps_mode", "cfr", "-video_track_timescale", "15360",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{DURATION:.3f}", "-movflags", "+faststart", str(FINAL),
        ]
    )


def orchestrate(preview_only: bool) -> None:
    storyboard = validate_storyboard()
    WORK.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    blender = shutil.which("blender")
    if not blender:
        raise RuntimeError("Blender is required")
    if preview_only:
        for old_preview in PREVIEW_DIR.glob("*.png"):
            old_preview.unlink()
    else:
        FRAMES_DIR.mkdir(parents=True, exist_ok=True)
        for old_frame in FRAMES_DIR.glob("frame_*.png"):
            old_frame.unlink()
        if VISUAL.exists():
            VISUAL.unlink()
    mode = "--preview" if preview_only else "--render-animation"
    run([blender, "-b", "--python", str(Path(__file__).resolve()), "--", "--blender-stage", mode])
    if preview_only:
        preview_count = len(list(PREVIEW_DIR.glob("*.png")))
        if preview_count != 18:
            raise RuntimeError(f"Blender preview failed closed: expected 18 frames, found {preview_count}")
        print(f"Preview frames: {PREVIEW_DIR}")
        return
    frame_files = sorted(FRAMES_DIR.glob("frame_*.png"))
    if len(frame_files) != FRAMES:
        raise RuntimeError(f"Blender animation failed closed: expected {FRAMES} PNGs, found {len(frame_files)}")
    run(
        [
            "ffmpeg", "-y", "-framerate", str(FPS), "-start_number", "1",
            "-i", str(FRAMES_DIR / "frame_%04d.png"),
            "-c:v", "libx264", "-preset", "fast", "-crf", "17",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-fps_mode", "cfr",
            "-t", f"{DURATION:.3f}", str(VISUAL),
        ]
    )
    if not VISUAL.exists() or VISUAL.stat().st_size < 1_000_000:
        raise RuntimeError("Visual encode failed closed: visual master missing or too small")
    composite_progression()
    synth_audio(storyboard)
    mux_final()
    print(f"Final: {FINAL}")


def blender_stage(preview: bool, render_animation: bool) -> None:
    import bpy
    from mathutils import Vector

    def sec(value: float) -> int:
        return max(1, round(value * FPS) + 1)

    def clear_scene() -> None:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
            pass

    def material(name: str, color: tuple[float, float, float, float], *, emission: float = 0.0, metallic: float = 0.0, roughness: float = 0.45):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = color
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission
        mat.diffuse_color = color
        return mat

    def rounded_cube(name: str, location, dimensions, mat, bevel: float = 0.16, parent=None):
        bpy.ops.mesh.primitive_cube_add(location=location)
        obj = bpy.context.object
        obj.name = name
        obj.dimensions = dimensions
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if bevel > 0:
            modifier = obj.modifiers.new("SoftEdges", "BEVEL")
            modifier.width = bevel
            modifier.segments = 3
        obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        return obj

    def sphere(name: str, location, scale, mat, parent=None, segments=24):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12, location=location)
        obj = bpy.context.object
        obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.data.materials.append(mat)
        bpy.ops.object.shade_smooth()
        if parent:
            obj.parent = parent
        return obj

    def text_obj(name: str, text: str, location, size: float, mat, parent=None, extrude: float = 0.018):
        bpy.ops.object.text_add(location=location, rotation=(math.radians(90), 0, 0))
        obj = bpy.context.object
        obj.name = name
        obj.data.body = text
        obj.data.align_x = "CENTER"
        obj.data.align_y = "CENTER"
        obj.data.size = size
        obj.data.extrude = extrude
        obj.data.bevel_depth = 0.008
        obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        return obj

    def key(obj, frame: int, prop: str) -> None:
        obj.keyframe_insert(data_path=prop, frame=frame)

    def set_interp(obj, mode: str = "BEZIER") -> None:
        if not obj.animation_data or not obj.animation_data.action:
            return
        action = obj.animation_data.action
        # Blender 5 uses layered Actions; Blender 4 exposed fcurves directly.
        if hasattr(action, "fcurves"):
            curves = action.fcurves
        else:
            if not action.layers or not action.layers[0].strips or not action.slots:
                return
            bag = action.layers[0].strips[0].channelbag(action.slots[0])
            curves = bag.fcurves if bag else []
        for curve in curves:
            for point in curve.keyframe_points:
                point.interpolation = mode

    def show_between(obj, start: float, end: float, scale=(1.0, 1.0, 1.0)) -> None:
        before = sec(max(0, start - 1 / FPS))
        on = sec(start)
        off = sec(end)
        after = sec(min(DURATION, end + 1 / FPS))
        obj.scale = (0.001, 0.001, 0.001)
        key(obj, before, "scale")
        obj.scale = scale
        key(obj, on, "scale")
        key(obj, off, "scale")
        obj.scale = (0.001, 0.001, 0.001)
        key(obj, after, "scale")
        set_interp(obj, "CONSTANT")

    def animate_transform(obj, points: list[tuple[float, tuple[float, float, float], tuple[float, float, float] | None, tuple[float, float, float] | None]], interp="BEZIER"):
        for time, loc, scale_value, rot in points:
            obj.location = loc
            key(obj, sec(time), "location")
            if scale_value is not None:
                obj.scale = scale_value
                key(obj, sec(time), "scale")
            if rot is not None:
                obj.rotation_euler = rot
                key(obj, sec(time), "rotation_euler")
        set_interp(obj, interp)

    def cylinder_to_target(name: str, origin, target, radius: float, mat, parent=None):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=1.0, location=origin)
        obj = bpy.context.object
        obj.name = name
        # Move mesh upward so the object's origin is one end of the cylinder.
        for vertex in obj.data.vertices:
            vertex.co.z += 0.5
        obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        constraint = obj.constraints.new("STRETCH_TO")
        constraint.target = target
        constraint.rest_length = 1.0
        constraint.volume = "NO_VOLUME"
        return obj

    def curve_between_targets(name: str, start_target, end_target, radius: float, mat):
        """Create a round two-point curve whose endpoints follow two empties.

        Hooked curve endpoints are deterministic across Blender versions and
        avoid StretchTo's version-specific local-axis behavior.
        """
        data = bpy.data.curves.new(name=f"{name}Curve", type="CURVE")
        data.dimensions = "3D"
        data.resolution_u = 2
        data.bevel_depth = radius
        data.bevel_resolution = 3
        data.resolution_u = 2
        spline = data.splines.new("POLY")
        spline.points.add(1)
        for point in spline.points:
            point.co = (0.0, 0.0, 0.0, 1.0)
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        data.materials.append(mat)
        for index, target in enumerate((start_target, end_target)):
            hook = obj.modifiers.new(f"Hook{index}", "HOOK")
            hook.object = target
            hook.vertex_indices_set([index])
        return obj

    def animated_poly_curve(name: str, start, end_points, radius: float, mat, *, parent=None, sag: float = 0.0):
        """Animate a three-point round spline directly from semantic endpoints."""
        data = bpy.data.curves.new(name=f"{name}Curve", type="CURVE")
        data.dimensions = "3D"
        data.resolution_u = 2
        data.bevel_depth = radius
        data.bevel_resolution = 3
        spline = data.splines.new("POLY")
        spline.points.add(2)
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        data.materials.append(mat)
        if parent:
            obj.parent = parent
        p0, p1, p2 = spline.points
        p0.co = (*start, 1.0)
        for time, end in end_points:
            middle = (
                (start[0] + end[0]) * 0.5,
                (start[1] + end[1]) * 0.5,
                (start[2] + end[2]) * 0.5 - sag,
            )
            p1.co = (*middle, 1.0)
            p2.co = (*end, 1.0)
            p1.keyframe_insert(data_path="co", frame=sec(time))
            p2.keyframe_insert(data_path="co", frame=sec(time))
        return obj

    def look_at(obj, target=(0, 0, 5)):
        direction = Vector(target) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    clear_scene()
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.eevee.taa_samples = 16
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 45
    scene.render.use_file_extension = True
    scene.world.color = (0.008, 0.012, 0.03)
    scene.view_settings.look = "AgX - Medium High Contrast"

    # Palette.
    bg = material("Background", (0.015, 0.025, 0.075, 1), roughness=0.8)
    panel = material("Panel", (0.035, 0.055, 0.14, 1), metallic=0.2, roughness=0.3)
    cyan = material("CyanGlow", (0.03, 0.9, 1.0, 1), emission=3.0)
    blue = material("Blue", (0.05, 0.28, 0.72, 1), metallic=0.25)
    violet = material("Violet", (0.45, 0.15, 0.9, 1), emission=1.2)
    white = material("White", (0.95, 0.98, 1.0, 1), emission=0.25)
    muted = material("Muted", (0.26, 0.34, 0.48, 1), roughness=0.7)
    green = material("Green", (0.12, 1.0, 0.32, 1), emission=2.2)
    yellow = material("Yellow", (1.0, 0.68, 0.06, 1), emission=1.2)
    red = material("Red", (1.0, 0.08, 0.08, 1), emission=2.5)
    fur = material("Fur", (0.48, 0.27, 0.13, 1), roughness=0.82)
    fur_light = material("FurLight", (0.68, 0.43, 0.23, 1), roughness=0.8)
    black = material("Black", (0.008, 0.01, 0.018, 1), roughness=0.3)
    hoodie = material("Hoodie", (0.04, 0.55, 0.78, 1), metallic=0.05, roughness=0.55)
    wood = material("Table", (0.36, 0.16, 0.07, 1), roughness=0.55)
    silver = material("Silver", (0.22, 0.29, 0.38, 1), metallic=0.75, roughness=0.23)
    screen = material("Screen", (0.008, 0.018, 0.032, 1), metallic=0.15, roughness=0.15)

    # Camera and lights.
    bpy.ops.object.camera_add(location=(0, -24, 5.0))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 18.0
    camera.data.lens = 50
    look_at(camera, (0, 0, 5.0))
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(-4, -9, 11))
    key_light = bpy.context.object
    key_light.data.energy = 1050
    key_light.data.shape = "DISK"
    key_light.data.size = 7
    look_at(key_light, (-0.5, 0, 3))
    bpy.ops.object.light_add(type="AREA", location=(5, -5, 7))
    fill_light = bpy.context.object
    fill_light.data.energy = 700
    fill_light.data.color = (0.25, 0.6, 1.0)
    fill_light.data.size = 5
    look_at(fill_light, (0, 0, 3))
    bpy.ops.object.light_add(type="POINT", location=(0, 1.5, 6))
    rim = bpy.context.object
    rim.data.energy = 500
    rim.data.color = (0.75, 0.2, 1.0)

    # Fixed stage: one camera, one table, no era portals.
    rounded_cube("BackWall", (0, 3.0, 5.0), (12.0, 0.7, 19.0), bg, 0.3)
    rounded_cube("CenterPanel", (0, 2.55, 5.2), (8.7, 0.26, 13.0), panel, 0.55)
    for x in (-4.45, 4.45):
        rounded_cube(f"NeonRail{x}", (x, 2.0, 5.2), (0.11, 0.11, 12.8), cyan, 0.05)
    for x, z in ((-3.8, 9.0), (3.8, 8.2), (-3.7, 1.0), (3.9, 2.0)):
        sphere(f"WallLight{x}{z}", (x, 2.0, z), (0.11, 0.08, 0.11), violet)
    rounded_cube("TableFront", (0, -0.5, -2.25), (12.0, 1.4, 3.4), wood, 0.35)
    rounded_cube("TableTrim", (0, -1.35, -0.55), (12.0, 0.18, 0.16), yellow, 0.07)

    # Persistent comparison tracker.
    tracker_x = [-3.45, -1.15, 1.15, 3.45]
    tracker_labels = ["1s", "1m", "10m", "1h"]
    tracker_plates = []
    for i, (x, label) in enumerate(zip(tracker_x, tracker_labels)):
        plate = rounded_cube(f"TrackerPlate{label}", (x, -2.4, 10.85), (1.75, 0.14, 0.84), muted, 0.25)
        tracker_plates.append(plate)
        text_obj(f"TrackerText{label}", label, (x, -2.58, 10.85), 0.52, white)
    text_obj("TrackerVs1", "vs", (-2.28, -2.58, 10.85), 0.23, muted)
    text_obj("TrackerVs2", "vs", (0.0, -2.58, 10.85), 0.23, muted)
    text_obj("TrackerVs3", "vs", (2.30, -2.58, 10.85), 0.23, muted)
    stage_windows = [(0.0, 8.5), (8.5, 19.0), (19.0, 31.5), (31.5, 49.8), (49.8, 52.0)]
    stage_indices = [0, 1, 2, 3, 0]
    for window, active_idx in zip(stage_windows, stage_indices):
        at = sec(window[0])
        for idx, plate in enumerate(tracker_plates):
            plate.scale = (1.08, 1.0, 1.08) if idx == active_idx else (1.0, 1.0, 1.0)
            key(plate, at, "scale")
        underline = rounded_cube(
            f"TrackerActive{active_idx}_{at}",
            (tracker_x[active_idx], -2.68, 10.34),
            (1.38, 0.10, 0.10),
            cyan,
            0.04,
        )
        show_between(underline, window[0], window[1], (1, 1, 1))
    for plate in tracker_plates:
        set_interp(plate, "CONSTANT")

    # Capybara mascot root.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-1.05, 0.0, 0.0))
    capy = bpy.context.object
    capy.name = "CapyRoot"
    body = sphere("Body", (0, 0.25, 0.55), (1.55, 0.85, 2.15), hoodie, capy)
    head = sphere("Head", (0, -0.08, 3.45), (1.65, 0.90, 1.36), fur, capy)
    snout = sphere("Snout", (0.0, -0.92, 3.10), (1.20, 0.42, 0.49), fur_light, capy)
    for x in (-1.05, 1.05):
        sphere(f"Ear{x}", (x, -0.02, 4.56), (0.29, 0.22, 0.31), fur, capy)
        sphere(f"EarInner{x}", (x, -0.25, 4.56), (0.14, 0.10, 0.15), fur_light, capy)
    eye_whites = []
    pupils = []
    brows = []
    for x in (-0.58, 0.58):
        eye_whites.append(sphere(f"EyeWhite{x}", (x, -0.88, 3.75), (0.40, 0.18, 0.34), white, capy))
        pupils.append(sphere(f"Pupil{x}", (x + 0.08, -1.08, 3.72), (0.15, 0.09, 0.18), black, capy))
        brow = rounded_cube(f"Brow{x}", (x, -1.10, 4.25), (0.62, 0.12, 0.10), black, 0.04, capy)
        brows.append(brow)
    nose = sphere("Nose", (0, -1.32, 3.37), (0.30, 0.16, 0.22), black, capy)
    neutral_mouth = rounded_cube("NeutralMouth", (0, -1.25, 2.88), (0.52, 0.10, 0.09), black, 0.04, capy)
    open_mouth = sphere("OpenMouth", (0, -1.24, 2.86), (0.34, 0.10, 0.42), black, capy)
    show_between(open_mouth, 30.0, 31.4, (1, 1, 1))
    # A second panic interval and airborne payoff use the same readable open mouth.
    panic_mouth = sphere("PanicMouth", (0, -1.25, 2.86), (0.45, 0.10, 0.58), black, capy)
    show_between(panic_mouth, 36.0, 49.1, (1, 1, 1))
    # Neutral mouth hidden when other mouths are visible.
    neutral_mouth.scale = (1, 1, 1)
    for time, value in ((0, (1, 1, 1)), (30.0, (0.001,)*3), (31.5, (1,1,1)), (36.0, (0.001,)*3), (49.2, (1,1,1))):
        neutral_mouth.scale = value
        key(neutral_mouth, sec(time), "scale")
    set_interp(neutral_mouth, "CONSTANT")

    # Arms track animated hand targets for true hand-object continuity.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(1.05, -0.55, 1.45))
    right_hand_target = bpy.context.object
    right_hand_target.name = "RightHandTarget"
    right_hand_target.parent = capy
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-1.20, -0.55, 0.5))
    left_hand_target = bpy.context.object
    left_hand_target.name = "LeftHandTarget"
    left_hand_target.parent = capy
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.95, -0.15, 1.55))
    right_shoulder_target = bpy.context.object
    right_shoulder_target.name = "RightShoulderTarget"
    right_shoulder_target.parent = capy
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-0.95, -0.15, 1.55))
    left_shoulder_target = bpy.context.object
    left_shoulder_target.name = "LeftShoulderTarget"
    left_shoulder_target.parent = capy
    # Hands remain world-space constraint followers. Parenting them as well would
    # apply the mascot root twice and create the detached-paw defect.
    right_hand = sphere("RightHand", (0, 0, 0), (0.46, 0.30, 0.46), fur_light)
    left_hand = sphere("LeftHand", (0, 0, 0), (0.46, 0.30, 0.46), fur_light)
    for hand, target in ((right_hand, right_hand_target), (left_hand, left_hand_target)):
        constraint = hand.constraints.new("COPY_LOCATION")
        constraint.target = target
        constraint.owner_space = "WORLD"
        constraint.target_space = "WORLD"

    # Same phone for every round.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(1.75, -1.0, 0.85))
    phone = bpy.context.object
    phone.name = "PhoneRoot"
    phone_body = rounded_cube("PhoneBody", (0, 0, 0), (2.1, 0.34, 3.55), silver, 0.30, phone)
    phone_screen = rounded_cube("PhoneScreen", (0, -0.24, 0.10), (1.78, 0.10, 3.06), screen, 0.22, phone)
    # Side port makes the repeated plug-in verb readable in a front-facing 9:16 shot.
    rounded_cube("PhonePort", (-1.03, -0.30, -0.38), (0.14, 0.12, 0.48), black, 0.05, phone)
    # Battery outline and fill are fixed to the phone; fill keys encode one scalar.
    rounded_cube("BatteryOutline", (0, -0.38, 0.20), (1.20, 0.08, 0.56), white, 0.10, phone)
    rounded_cube("BatteryInner", (0, -0.46, 0.20), (0.98, 0.06, 0.34), black, 0.07, phone)
    battery_fill = rounded_cube("BatteryFill", (-0.47, -0.53, 0.20), (0.94, 0.05, 0.28), green, 0.05, phone)
    # Origin at left edge so x-scale grows rightward.
    for vertex in battery_fill.data.vertices:
        vertex.co.x += 0.47
    battery_fill.location.x = -0.47

    # Percentage labels: large, simple, and mutually exclusive.
    pct_specs = [
        ("Pct1A", "1%", 0.0, 1.2), ("Pct2", "2%", 1.2, 8.5),
        ("Pct1B", "1%", 8.5, 10.0), ("Pct15", "15%", 10.0, 19.0),
        ("Pct1C", "1%", 19.0, 20.5), ("Pct100A", "100%", 20.5, 31.5),
        ("Pct1D", "1%", 31.5, 33.2), ("Pct100B", "100%", 33.2, 48.2),
        ("Pct1Loop", "1%", 49.2, 52.0),
    ]
    for name, label, start, end in pct_specs:
        obj = text_obj(name, label, (0, -0.56, -0.60), 0.60 if label != "100%" else 0.45, white, phone)
        show_between(obj, start, end, (1, 1, 1))

    fill_points = [
        (0.0, 0.01), (1.2, 0.02), (8.49, 0.02),
        (8.5, 0.01), (10.0, 0.15), (18.99, 0.15),
        (19.0, 0.01), (20.5, 0.15), (26.5, 1.0), (31.49, 1.0),
        (31.5, 0.01), (33.2, 0.15), (36.0, 1.0), (48.19, 1.0),
        (49.2, 0.01), (52.0, 0.01),
    ]
    for time, amount in fill_points:
        battery_fill.scale.x = max(0.01, amount)
        key(battery_fill, sec(time), "scale")
    set_interp(battery_fill, "LINEAR")

    # Cable/plug and repeated plug-in action.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-4.8, -1.15, 0.48))
    cable_anchor = bpy.context.object
    cable_anchor.name = "CableAnchor"
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-0.25, -1.35, 0.48))
    plug_target = bpy.context.object
    plug_target.name = "PlugTarget"
    plug = rounded_cube("PlugHead", (0, 0, 0), (0.52, 0.30, 0.46), silver, 0.08)
    constraint = plug.constraints.new("COPY_LOCATION")
    constraint.target = plug_target
    # Plug keyframes: same starting point and exact endpoint every round.
    approach = (-0.25, -1.35, 0.48)
    inserted = (0.67, -1.35, 0.48)
    retract = (-0.38, -1.35, 0.48)
    plug_points = [
        (0.0, approach), (0.85, inserted), (7.8, inserted), (8.25, retract),
        (8.5, approach), (9.45, inserted), (18.3, inserted), (18.75, retract),
        (19.0, approach), (20.0, inserted), (30.8, inserted), (31.25, retract),
        (31.5, approach), (32.55, inserted), (42.0, inserted), (42.25, retract),
        (49.8, approach), (52.0, inserted),
    ]
    for time, loc in plug_points:
        plug_target.location = loc
        key(plug_target, sec(time), "location")
    set_interp(plug_target, "BEZIER")
    animated_poly_curve(
        "ChargingCable",
        tuple(cable_anchor.location),
        plug_points,
        0.16,
        cyan,
        sag=0.32,
    )

    # Right hand follows the repeated plugging movement; left hand rests then joins the final struggle.
    for time, loc in plug_points:
        # Convert world plug motion into capy-root local coordinates; the paw
        # stays just behind the plug so the cable, hand and phone form one line.
        right_hand_target.location = (loc[0] + 0.65, loc[1] + 0.35, loc[2] + 0.05)
        key(right_hand_target, sec(time), "location")
    left_hand_points = [
        (0.0, (-1.20, -0.55, 0.50)), (31.5, (-1.20, -0.55, 0.50)),
        (36.0, (1.55, -0.55, 0.35)), (42.0, (1.75, -0.75, 0.45)),
        (46.0, (1.9, -0.75, 2.4)), (48.0, (2.0, -0.75, 4.5)),
        (48.4, (-1.20, -0.55, 0.50)), (52.0, (-1.20, -0.55, 0.50)),
    ]
    for time, loc in left_hand_points:
        left_hand_target.location = loc
        key(left_hand_target, sec(time), "location")
    set_interp(left_hand_target, "BEZIER")
    right_hand_points = [
        (time, (loc[0] + 0.65, loc[1] + 0.35, loc[2] + 0.05))
        for time, loc in plug_points
    ]
    animated_poly_curve(
        "RightArm",
        (0.95, -0.15, 1.55),
        right_hand_points,
        0.31,
        fur,
        parent=capy,
        sag=0.18,
    )
    animated_poly_curve(
        "LeftArm",
        (-0.95, -0.15, 1.55),
        left_hand_points,
        0.31,
        fur,
        parent=capy,
        sag=0.18,
    )

    # Semantic pose/reaction state, with an idle bounce so no frame is merely static UI motion.
    for frame in range(1, FRAMES + 1, 15):
        time = (frame - 1) / FPS
        z = 0.06 * math.sin(time * math.pi * 1.2)
        rot = 0.018 * math.sin(time * math.pi * 0.75)
        capy.location = (-1.05, 0.0, z)
        capy.rotation_euler = (0, 0, rot)
        key(capy, frame, "location")
        key(capy, frame, "rotation_euler")
    # Override major reactions and final lift/fall.
    reaction_points = [
        (5.8, (-1.05, 0, -0.10), (1,1,1), (0,0,-0.08)),
        (7.2, (-1.05, 0, -0.18), (1,1,1), (0,0,0.08)),
        (16.5, (-1.05, 0, 0.08), (1,1,1), (0,0,-0.05)),
        (26.5, (-1.05, 0, 0.20), (1.05,1.05,1.05), (0,0,0.08)),
        (28.7, (-1.05, 0, 0.0), (1,1,1), (0,0,-0.04)),
        (36.0, (-1.05, 0, 0.05), (1,1,1), (0,0,-0.08)),
        (42.0, (-1.05, 0, 0.15), (1,1,1), (0,0,0.06)),
        (46.0, (-1.05, 0, 2.0), (1,1,1), (0,0,-0.12)),
        (48.0, (-1.05, 0, 4.2), (1,1,1), (0,0,0.16)),
        (48.45, (-1.05, 0, -1.7), (1,1,1), (0,0,-0.22)),
        (49.4, (-1.05, 0, -0.2), (1,1,1), (0,0,0.06)),
        (50.2, (-1.05, 0, 0), (1,1,1), (0,0,0)),
        (52.0, (-1.05, 0, 0), (1,1,1), (0,0,0)),
    ]
    animate_transform(capy, reaction_points, "BEZIER")

    # Eyebrows and pupils encode disappointment -> hope -> celebration -> panic.
    for brow in brows:
        brow.rotation_euler.z = 0
        key(brow, sec(0), "rotation_euler")
        brow.rotation_euler.z = 0.22 if brow.location.x < 0 else -0.22
        key(brow, sec(5.8), "rotation_euler")
        brow.rotation_euler.z = -0.12 if brow.location.x < 0 else 0.12
        key(brow, sec(16.5), "rotation_euler")
        brow.rotation_euler.z = 0
        key(brow, sec(26.5), "rotation_euler")
        brow.rotation_euler.z = -0.35 if brow.location.x < 0 else 0.35
        key(brow, sec(36.0), "rotation_euler")
        brow.rotation_euler.z = 0.30 if brow.location.x < 0 else -0.30
        key(brow, sec(49.0), "rotation_euler")
        brow.rotation_euler.z = 0
        key(brow, sec(51.5), "rotation_euler")
        set_interp(brow, "BEZIER")
    for pupil in pupils:
        for time, dx, dz in ((0, 0.18, -0.02), (5.8, 0.20, -0.12), (16.5, 0.20, 0.02), (28.5, 0.25, 0.08), (36, 0.28, 0.14), (48.2, 0.0, 0.22), (50.0, 0.18, -0.02)):
            pupil.location.x = (-0.58 if "-0.58" in pupil.name else 0.58) + dx
            pupil.location.z = 3.72 + dz
            key(pupil, sec(time), "location")
        set_interp(pupil, "BEZIER")

    # Phone warmth and wobble; scale is the physical consequence, not decorative UI.
    phone_points = [
        (0.0, (1.75,-1.0,0.85), (1,1,1), (0,0,0)),
        (27.5, (1.75,-1.0,0.85), (1,1,1), (0,0,-0.02)),
        (28.5, (1.75,-1.0,0.85), (1.03,1.03,1.03), (0,0,0.05)),
        (29.5, (1.75,-1.0,0.85), (1,1,1), (0,0,-0.05)),
        (30.5, (1.75,-1.0,0.85), (1.04,1.04,1.04), (0,0,0.06)),
        (31.5, (1.75,-1.0,0.85), (1,1,1), (0,0,0)),
        (36.0, (1.75,-1.0,0.85), (1.10,1.10,1.10), (0,0,0.04)),
        (39.0, (1.75,-1.0,0.95), (1.35,1.25,1.35), (0,0,-0.06)),
        (42.0, (1.75,-1.0,1.15), (1.75,1.45,1.75), (0,0,0.08)),
        (45.0, (1.75,-1.0,2.50), (2.15,1.65,2.15), (0,0,-0.12)),
        (48.0, (1.75,-1.0,5.45), (2.55,1.85,2.55), (0,0,0.16)),
        (48.18, (1.75,-1.0,5.45), (0.08,0.08,0.08), (0,0,0)),
        (49.1, (1.75,-1.0,0.85), (0.08,0.08,0.08), (0,0,0)),
        (49.25, (1.75,-1.0,0.85), (1,1,1), (0,0,0)),
        (52.0, (1.75,-1.0,0.85), (1,1,1), (0,0,0)),
    ]
    animate_transform(phone, phone_points, "BEZIER")

    # Heat waves and pop flash/debris are tied to the phone event.
    for i, x in enumerate((0.9, 1.75, 2.6)):
        wave = text_obj(f"HeatWave{i}", "~", (x, -2.0, 3.2 + 0.2*i), 0.8, yellow)
        show_between(wave, 27.5 + i*0.16, 31.4, (1,1,1))
        wave2 = text_obj(f"HeatWaveFinal{i}", "~", (x, -2.0, 3.2 + 0.25*i), 1.0, red)
        show_between(wave2, 35.0 + i*0.12, 48.15, (1,1,1))
        animate_transform(wave2, [(35.0,(x,-2,3.2+i*.25),(1,1,1),(0,0,0)), (48.0,(x,-2,7.5+i*.3),(1.3,1.3,1.3),(0,0,0))], "LINEAR")
    flash = sphere("PopFlash", (1.75, -2.2, 5.45), (2.2, 0.2, 2.2), white)
    show_between(flash, 48.0, 48.22, (1,1,1))
    for i in range(14):
        angle = i * 2 * math.pi / 14
        piece = rounded_cube(f"Debris{i}", (1.75,-2.1,5.45), (0.22,0.10,0.22), yellow if i%2 else cyan, 0.06)
        show_between(piece, 48.02, 49.6, (1,1,1))
        animate_transform(piece, [
            (48.02,(1.75,-2.1,5.45),(1,1,1),(0,0,0)),
            (49.6,(1.75+math.cos(angle)*4.2,-2.1,5.45+math.sin(angle)*4.2),(0.35,0.35,0.35),(0,0,angle*2)),
        ], "LINEAR")

    # Compact story-native triple CTA, each prompt visible alone while swelling continues.
    cta_specs = [("LIKE",38.4,39.4), ("SUB",39.5,40.5), ("COMMENT 1H",40.6,41.8)]
    for idx, (label, start, end) in enumerate(cta_specs):
        plate = rounded_cube(f"CTAPlate{idx}", (3.65,-3.2,-2.3), (2.3,0.12,0.70), violet, 0.22)
        show_between(plate, start, end, (1,1,1))
        cta = text_obj(f"CTAText{idx}", label, (3.65,-3.35,-2.3), 0.33 if len(label)>4 else 0.45, white)
        show_between(cta, start, end, (1,1,1))

    # Moving but unobtrusive watermark.
    watermark = text_obj("Watermark", "@ZAPBARA", (-4.0,-3.4,-4.2), 0.24, muted)
    animate_transform(watermark, [
        (0.0,(-4.0,-3.4,-4.2),(1,1,1),(0,0,0)),
        (18.0,(4.0,-3.4,-4.2),(1,1,1),(0,0,0)),
        (34.0,(4.0,-3.4,8.9),(1,1,1),(0,0,0)),
        (52.0,(-4.0,-3.4,-4.2),(1,1,1),(0,0,0)),
    ], "LINEAR")

    # Save reproducible scene before rendering.
    BLEND_FILE.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))

    if preview:
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        for timestamp in (0.0, 0.3, 1.0, 6.0, 9.0, 17.0, 20.0, 27.0, 31.0, 32.0, 36.0, 39.0, 42.0, 46.0, 48.0, 49.0, 50.0, 51.8):
            scene.frame_set(sec(timestamp))
            scene.render.filepath = str(PREVIEW_DIR / f"{timestamp:05.1f}.png")
            bpy.ops.render.render(write_still=True)
        return

    if render_animation:
        FRAMES_DIR.mkdir(parents=True, exist_ok=True)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(FRAMES_DIR / "frame_")
        bpy.ops.render.render(animation=True)


def main() -> None:
    if "--blender-stage" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
        blender_stage(preview="--preview" in args, render_animation="--render-animation" in args)
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Render critical preview frames only")
    ns = parser.parse_args()
    orchestrate(ns.preview)


if __name__ == "__main__":
    main()
