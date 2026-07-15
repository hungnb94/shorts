import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_hardknocks_v7 as renderer  # noqa: E402
from render_hardknocks_v7 import (  # noqa: E402
    CAPTIONS,
    CHECKS,
    FINAL,
    FINISH_PAD,
    FPS,
    HOOK_CAPTIONS,
    PEXELS,
    PEXELS_OVERLAYS,
    PEXELS_PRODUCT,
    PEXELS_TEAM,
    POST_SPEED,
    RAW_DURATION,
    SOURCE,
    SOURCE_DURATION,
    TIMELINE,
    TOTAL_FRAMES,
    final_duration,
    finish_audio_filter,
    finish_video_filter,
    source_usage_ratio,
    tts_lines,
    validate_timeline,
)


class HardKnocksV7RendererTests(unittest.TestCase):
    def test_render_pipeline_exposes_required_operations(self):
        required = {
            "ass_time",
            "composite_pexels_overlays",
            "extract_checks",
            "finish",
            "generate_music_and_sfx",
            "main",
            "make_subtitles",
            "mix_raw",
            "probe",
            "render_source_clip",
            "render_video_timeline",
            "require_inputs",
            "source_video_filter",
            "validate_output",
        }
        missing = sorted(name for name in required if not hasattr(renderer, name))
        self.assertEqual(missing, [], f"Missing render operations: {missing}")

    def test_ass_time_formats_subtitle_timestamps(self):
        self.assertEqual(renderer.ass_time(0.0), "0:00:00.00")
        self.assertEqual(renderer.ass_time(65.25), "0:01:05.25")

    def test_probe_reads_the_real_4k_source(self):
        info = renderer.probe(SOURCE)
        video_streams = [
            stream for stream in info.get("streams", []) if stream.get("codec_type") == "video"
        ]
        self.assertTrue(video_streams, "ffprobe result must contain a video stream")
        video = video_streams[0]
        self.assertEqual((video["width"], video["height"]), (3840, 2160))

    def test_require_inputs_creates_render_directories(self):
        renderer.require_inputs()
        self.assertTrue(renderer.WORK.is_dir())
        self.assertTrue(renderer.PANELS.is_dir())
        self.assertTrue(CHECKS.is_dir())
        self.assertTrue(FINAL.parent.is_dir())

    def test_source_filter_uses_zoom_crop_without_an_unneeded_black_mask(self):
        vf = renderer.source_video_filter(TIMELINE[0])
        self.assertIn("scale=3414:1920", vf)
        self.assertIn("crop=1080:1920", vf)
        self.assertNotIn("drawbox=", vf)
        self.assertIn("fps=30", vf)
        self.assertIn("format=yuv420p", vf)

    def test_subtitle_builder_writes_value_add_styles_and_citation(self):
        renderer.require_inputs()
        subtitles = renderer.make_subtitles()
        self.assertTrue(subtitles.is_file())
        text = subtitles.read_text(encoding="utf-8")
        self.assertIn("Style: Editorial", text)
        self.assertIn("Style: Citation", text)
        self.assertIn("THE WORST GRADE", text)
        self.assertIn("SOURCE: THE SCHOOL OF HARD KNOCKS", text)
        source_style = next(line for line in text.splitlines() if line.startswith("Style: Source,"))
        self.assertEqual(source_style.split(",")[18], "2")

    def test_production_timeline_passes_transformative_gate(self):
        self.assertTrue(TIMELINE, "Production timeline must not be empty")
        validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
        self.assertLessEqual(source_usage_ratio(TIMELINE), 0.5)
        self.assertGreaterEqual(final_duration(), 45.0)
        self.assertLessEqual(final_duration(), 60.0)

    def test_four_source_excerpts_are_short_and_in_story_order(self):
        source_clips = [clip for clip in TIMELINE if clip.kind == "source"]
        self.assertEqual(
            [clip.name for clip in source_clips],
            ["rejection_focus", "funding_proof", "scale_proof", "rebuild_rule"],
        )
        self.assertTrue(all(clip.frames / FPS < 15.0 for clip in source_clips))

    def test_source_boundaries_preserve_every_required_payoff(self):
        clips = {clip.name: clip for clip in TIMELINE}
        expected = {
            "rejection_focus": (188.60, 199.32, 199.40),
            "funding_proof": (299.16, 313.20, 313.74),
            "scale_proof": (354.62, 364.28, 364.40),
            "rebuild_rule": (760.60, 774.00, 774.04),
        }
        self.assertEqual(set(clips), set(expected))
        for name, (expected_start, required_end, next_word_start) in expected.items():
            clip = clips[name]
            self.assertAlmostEqual(clip.source_start, expected_start, places=2)
            source_end = clip.source_start + clip.frames / FPS
            self.assertGreaterEqual(source_end, required_end, name)
            self.assertLess(source_end, next_word_start, name)

    def test_hook_starts_on_moving_todd_and_caption_arrives_by_point_two(self):
        self.assertTrue(TIMELINE, "Production timeline must not be empty")
        self.assertEqual(TIMELINE[0].name, "rejection_focus")
        self.assertEqual(TIMELINE[0].kind, "source")
        self.assertGreaterEqual(TIMELINE[0].crop_focus, 0.20)
        self.assertLessEqual(TIMELINE[0].crop_focus, 0.35)
        self.assertTrue(HOOK_CAPTIONS, "Hook captions must not be empty")
        self.assertLessEqual(HOOK_CAPTIONS[0][0], 0.2)
        self.assertEqual(HOOK_CAPTIONS[0][2], "THE WORST GRADE")

    def test_caption_schedule_contains_all_editorial_value_adds(self):
        caption_text = " ".join(item[3] for item in CAPTIONS)
        for phrase in (
            "ONE CORE PRODUCT",
            "$50K CASH + $50K SBA",
            "SOURCE-REPORTED",
            "CRAVABLE PRODUCT",
            "BUILD A TEAM",
            "SCALE IT",
        ):
            self.assertIn(phrase, caption_text)

    def test_approved_pexels_assets_are_exact_and_unbranded(self):
        self.assertEqual(PEXELS, PEXELS_PRODUCT)
        self.assertEqual(PEXELS_PRODUCT.name, "fried_chicken_9829921.mp4")
        self.assertEqual(PEXELS_TEAM.name, "restaurant_team_4253352.mp4")
        self.assertTrue(PEXELS_OVERLAYS, "Evidence overlays must not be empty")
        overlay_assets = {overlay.asset.name for overlay in PEXELS_OVERLAYS}
        self.assertEqual(overlay_assets, {PEXELS_PRODUCT.name, PEXELS_TEAM.name})

    def test_pexels_never_replaces_face_inside_first_ten_seconds(self):
        self.assertTrue(PEXELS_OVERLAYS, "Evidence overlays must not be empty")
        first_final_time = min(
            overlay.start_frame / FPS / POST_SPEED for overlay in PEXELS_OVERLAYS
        )
        self.assertGreaterEqual(first_final_time, 10.0)
        self.assertTrue(all(overlay.mode in {"corner", "fullscreen"} for overlay in PEXELS_OVERLAYS))

    def test_selected_speech_is_already_tight_so_speedup_is_mild(self):
        self.assertEqual(POST_SPEED, 1.02)
        self.assertEqual(tts_lines(), [])

    def test_final_speedup_flushes_the_last_spoken_word(self):
        self.assertEqual(
            finish_audio_filter(),
            (
                f"atempo={POST_SPEED},apad=pad_dur=0.35,"
                f"atrim=duration={RAW_DURATION / POST_SPEED + 0.35:.6f}"
            ),
        )
        self.assertGreaterEqual(FINISH_PAD, 0.70)
        self.assertTrue(finish_video_filter().startswith("tpad="))
        self.assertIn(f"setpts=PTS/{POST_SPEED}", finish_video_filter())

    def test_source_usage_is_a_small_fraction_of_the_original(self):
        used_seconds = sum(clip.frames for clip in TIMELINE) / FPS
        self.assertLess(used_seconds, SOURCE_DURATION * 0.5)
        self.assertLess(source_usage_ratio(TIMELINE), 0.06)

    def test_paths_target_v7_artifacts(self):
        self.assertEqual(SOURCE.name, "n5EmUiLNVjg.mp4")
        self.assertEqual(FINAL.name, "2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4")
        self.assertEqual(CHECKS.name, "checks")


if __name__ == "__main__":
    unittest.main()