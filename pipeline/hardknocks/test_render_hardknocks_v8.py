import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_hardknocks_v8 as renderer  # noqa: E402
from render_hardknocks_v8 import (  # noqa: E402
    CAPTIONS,
    CHECKS,
    EVIDENCE_OVERLAYS,
    FINAL,
    FINISH_PAD,
    FPS,
    HOOK_CAPTIONS,
    POST_SPEED,
    RAW_DURATION,
    SOURCE,
    SOURCE_DURATION,
    TIMELINE,
    TOTAL_FRAMES,
    final_duration,
    source_usage_ratio,
    tts_lines,
    validate_timeline,
)


class HardKnocksV8RendererTests(unittest.TestCase):
    def test_render_pipeline_exposes_required_operations(self):
        required = {
            "ass_time",
            "composite_evidence_overlays",
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

    def test_probe_reads_the_real_4k_source(self):
        info = renderer.probe(SOURCE)
        video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (3840, 2160))
        self.assertEqual(video["codec_name"], "av1")

    def test_timeline_is_exact_story_order_and_every_excerpt_is_short(self):
        expected_names = [
            "weird_hook",
            "overnight_question",
            "started_at_nine",
            "not_a_job",
            "nine_ten_years",
            "ten_thousand_hours",
            "goosebumps_work",
            "vine_setup",
            "six_second_fit",
            "personal_question",
            "thirty_million",
            "company_question",
            "prime_billion",
            "scale_question",
            "great_partners",
            "influencer_value",
        ]
        self.assertEqual([clip.name for clip in TIMELINE], expected_names)
        self.assertTrue(all(clip.frames / FPS < 15.0 for clip in TIMELINE))
        validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)

    def test_source_boundaries_preserve_required_payoffs(self):
        expected = {
            "weird_hook": (776.36, 779.28),
            "overnight_question": (756.02, 761.82),
            "started_at_nine": (761.84, 768.52),
            "not_a_job": (768.58, 771.24),
            "nine_ten_years": (779.28, 783.64),
            "ten_thousand_hours": (783.70, 788.64),
            "goosebumps_work": (788.64, 791.18),
            "vine_setup": (791.64, 796.00),
            "six_second_fit": (796.00, 799.78),
            "personal_question": (802.12, 805.28),
            "thirty_million": (810.42, 811.90),
            "company_question": (812.72, 814.64),
            "prime_billion": (815.96, 818.24),
            "scale_question": (818.30, 820.28),
            "great_partners": (820.40, 821.82),
            "influencer_value": (822.14, 827.28),
        }
        clips = {clip.name: clip for clip in TIMELINE}
        self.assertEqual(set(clips), set(expected))
        for name, (start, required_end) in expected.items():
            clip = clips[name]
            self.assertAlmostEqual(clip.source_start, start, places=2)
            actual_end = clip.source_start + clip.frames / FPS
            self.assertGreaterEqual(actual_end + (1 / FPS), required_end, name)
            self.assertLessEqual(actual_end, required_end + (1 / FPS), name)

    def test_active_speaker_reframing_and_semantic_zoom_are_explicit(self):
        host = {"overnight_question", "personal_question", "company_question", "scale_question"}
        close = {
            "weird_hook",
            "not_a_job",
            "ten_thousand_hours",
            "goosebumps_work",
            "six_second_fit",
            "thirty_million",
            "prime_billion",
            "scale_question",
            "great_partners",
        }
        for clip in TIMELINE:
            if clip.name in host:
                self.assertEqual(clip.speaker, "host")
                self.assertGreaterEqual(clip.crop_focus, 0.66)
                self.assertLessEqual(clip.crop_focus, 0.74)
            else:
                self.assertEqual(clip.speaker, "logan")
                self.assertGreaterEqual(clip.crop_focus, 0.32)
                self.assertLessEqual(clip.crop_focus, 0.40)
            expected_framing = "close" if clip.name in close else "medium"
            self.assertEqual(clip.framing, expected_framing)
            self.assertEqual(clip.zoom, 1.36 if expected_framing == "close" else 1.20)

    def test_crop_filter_removes_source_subtitles_without_black_mask(self):
        vf = renderer.source_video_filter(TIMELINE[0])
        self.assertIn("scale=3414:1920", vf)
        self.assertIn("crop=1080:1920", vf)
        self.assertIn("scale=1469:2611", vf)
        self.assertIn("crop=1080:1920:(in_w-1080)/2:0", vf)
        self.assertNotIn("drawbox=", vf)

    def test_hook_starts_on_moving_logan_and_caption_arrives_by_point_two(self):
        self.assertEqual(TIMELINE[0].name, "weird_hook")
        self.assertEqual(TIMELINE[0].speaker, "logan")
        self.assertEqual(TIMELINE[0].framing, "close")
        self.assertTrue(HOOK_CAPTIONS)
        self.assertLessEqual(HOOK_CAPTIONS[0][0], 0.2)
        self.assertEqual(HOOK_CAPTIONS[0][2], "YOU GUYS ARE WEIRD")

    def test_evidence_plan_is_multi_source_and_stays_out_of_protected_window(self):
        self.assertEqual(
            [overlay.name for overlay in EVIDENCE_OVERLAYS],
            [
                "childhood_home",
                "childhood_brothers",
                "vine_archive",
                "prime_product",
                "partner_handshake",
            ],
        )
        self.assertEqual(
            [overlay.mode for overlay in EVIDENCE_OVERLAYS],
            ["topcrop", "topcrop", "topcrop", "fullscreen", "fullscreen"],
        )
        first_final = min(overlay.start_frame / FPS / POST_SPEED for overlay in EVIDENCE_OVERLAYS)
        self.assertGreaterEqual(first_final, 10.0)
        assets = {overlay.asset.name for overlay in EVIDENCE_OVERLAYS}
        self.assertEqual(
            assets,
            {
                "logan_childhood_home_R9ve03SbYqg.mp4",
                "logan_vines_cXNLpsB4zw4.mp4",
                "prime_commercial_ebha0MzwtU8.mp4",
                "contract_signing_7981954.mp4",
            },
        )
        evidence_seconds = sum(overlay.frames for overlay in EVIDENCE_OVERLAYS) / FPS
        self.assertGreaterEqual(evidence_seconds / RAW_DURATION, 0.25)
        self.assertLessEqual(evidence_seconds / RAW_DURATION, 0.35)
        self.assertEqual(
            [overlay.crop_focus for overlay in EVIDENCE_OVERLAYS[:3]],
            [0.65, 0.28, 0.42],
        )

    def test_external_excerpt_pipeline_uses_accurate_post_input_seek(self):
        self.assertTrue(hasattr(renderer, "render_evidence_excerpt"))
        self.assertEqual(renderer.EVIDENCE_OVERLAYS[0].source_offset, 160.4)
        self.assertEqual(renderer.EVIDENCE_OVERLAYS[2].source_offset, 13.2)

    def test_caption_schedule_contains_story_value_adds_and_source_citations(self):
        caption_text = " ".join(item[3] for item in CAPTIONS)
        for phrase in (
            "9-10 YEARS",
            "10,000 HOURS",
            "6-SECOND LOOPS",
            "ABOUT $30 MILLION",
            "PRIME: $1.2 BILLION",
            "GREAT PARTNERS",
            "SOURCE: SCHOOL OF HARD KNOCKS",
            "ARCHIVE: GRAHAM BENSINGER",
            "ARCHIVE: ODDLY SATISFYING MOTION",
            "SOURCE: LOGAN PAUL / PRIME",
            "ILLUSTRATION: PEXELS",
        ):
            self.assertIn(phrase, caption_text)

    def test_transformative_gate_duration_and_usage_pass(self):
        self.assertLessEqual(source_usage_ratio(TIMELINE), 0.5)
        self.assertGreaterEqual(final_duration(), 45.0)
        self.assertLessEqual(final_duration(), 60.0)
        self.assertEqual(tts_lines(), [])
        self.assertEqual(POST_SPEED, 1.03)
        self.assertGreaterEqual(FINISH_PAD, 0.70)

    def test_retention_finish_settings_are_bounded(self):
        self.assertEqual(renderer.POST_SPEED, 1.03)
        self.assertLessEqual(renderer.POST_SPEED, 1.10)
        self.assertGreater(renderer.FINISH_PAD, 0.0)
        self.assertGreaterEqual(renderer.AUDIO_FINISH_PAD, 0.65)

    def test_paths_target_v8_artifacts(self):
        self.assertEqual(SOURCE.name, "ALvduf2Rz_c.mp4")
        self.assertEqual(FINAL.name, "2026-07-16-hardknocks_v8_logan_platform_fit.mp4")
        self.assertEqual(CHECKS.name, "checks")
        self.assertAlmostEqual(SOURCE_DURATION, 956.383492, places=3)


if __name__ == "__main__":
    unittest.main()
