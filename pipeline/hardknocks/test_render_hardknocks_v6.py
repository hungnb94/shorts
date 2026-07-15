import unittest

from render_hardknocks_v6 import (
    FPS,
    FINISH_PAD,
    HOOK_CAPTIONS,
    PEXELS,
    PEXELS_OVERLAYS,
    POST_SPEED,
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


class HardKnocksV6RendererTests(unittest.TestCase):
    def test_production_timeline_passes_transformative_gate(self):
        validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
        self.assertLessEqual(source_usage_ratio(TIMELINE), 0.5)
        self.assertGreaterEqual(final_duration(), 45.0)
        self.assertLessEqual(final_duration(), 60.0)

    def test_source_clips_are_short_and_multi_clip(self):
        source_clips = [clip for clip in TIMELINE if clip.kind == "source"]
        self.assertGreaterEqual(len(source_clips), 10)
        self.assertTrue(all(clip.frames / FPS < 15.0 for clip in source_clips))
        self.assertGreater(len({clip.source_start for clip in source_clips}), 8)

    def test_bankruptcy_sting_starts_on_the_complete_spoken_phrase(self):
        hook_broke = next(clip for clip in TIMELINE if clip.name == "hook_broke")
        self.assertEqual(hook_broke.source_start, 1488.30)

    def test_original_voice_payoffs_are_not_cut_off(self):
        public = next(clip for clip in TIMELINE if clip.name == "public_a")
        humility = next(clip for clip in TIMELINE if clip.name == "humility_b")
        trust = next(clip for clip in TIMELINE if clip.name == "trust_a")
        trust_end = next(clip for clip in TIMELINE if clip.name == "trust_f")
        self.assertEqual(public.source_start, 1489.32)
        assert humility.source_start is not None
        self.assertGreaterEqual(humility.source_start + humility.frames / FPS, 1519.30)
        self.assertEqual(trust.source_start, 1591.52)
        assert trust_end.source_start is not None
        self.assertGreaterEqual(trust_end.source_start + trust_end.frames / FPS, 1607.88)

    def test_hook_starts_on_moving_source_and_caption_is_visible_by_point_two(self):
        self.assertEqual(TIMELINE[0].kind, "source")
        self.assertGreater(TIMELINE[0].frames, 0)
        self.assertLessEqual(HOOK_CAPTIONS[0][0], 0.2)
        self.assertEqual(HOOK_CAPTIONS[0][2], "THEY CALLED HIM")

    def test_fullscreen_pexels_never_replaces_face_in_first_ten_seconds(self):
        self.assertTrue(all(clip.kind == "source" for clip in TIMELINE))
        self.assertGreaterEqual(min(window[0] for window in PEXELS_OVERLAYS) / POST_SPEED, 10.0)

    def test_original_voice_story_has_required_sections(self):
        names = {clip.name for clip in TIMELINE}
        self.assertTrue(
            {
                "context_fired",
                "context_doubt",
                "answer_absolutely",
                "public_a",
                "revenue_a",
                "listen_a",
                "humility_a",
                "trust_a",
                "trust_f",
            }.issubset(names)
        )

    def test_approved_pexels_asset_is_unbranded_warehouse_footage(self):
        self.assertEqual(PEXELS.name, "inventory_worker_7018664.mp4")

    def test_no_neural_voice_interrupts_the_interview(self):
        self.assertEqual(tts_lines(), [])

    def test_final_speedup_flushes_the_last_spoken_word(self):
        self.assertEqual(finish_audio_filter(), f"atempo={POST_SPEED}")
        self.assertGreaterEqual(FINISH_PAD, 0.70)
        self.assertTrue(finish_video_filter().startswith("tpad="))
        self.assertIn(f"setpts=PTS/{POST_SPEED}", finish_video_filter())

    def test_source_usage_is_a_small_fraction_of_the_original(self):
        used_seconds = sum(clip.frames for clip in TIMELINE) / FPS
        self.assertLess(used_seconds, SOURCE_DURATION * 0.5)


if __name__ == "__main__":
    unittest.main()
