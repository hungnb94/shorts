import unittest

from render_laundromat_v1 import (
    AUDIO_PIECES,
    Financials,
    REQUIRED_DIALOGUE_WINDOWS,
    TIMELINE,
    TOTAL_FRAMES,
    VISUAL_RECIPES,
    TimelineClip,
    financial_summary,
    music_volume_expression,
    source_share,
    validate_timeline,
)


class LaundromatRendererTests(unittest.TestCase):
    def test_music_stays_ducked_under_dialogue_and_returns_for_tail(self):
        self.assertEqual(
            music_volume_expression(),
            "volume='if(gte(t,49.60),1.00,0.035)':eval=frame",
        )
        self.assertEqual(
            REQUIRED_DIALOGUE_WINDOWS,
            [(20.88, 25.00, -24.0), (43.02, 49.60, -24.0)],
        )

    def test_audio_pieces_end_on_verified_sentence_boundaries(self):
        self.assertEqual(
            [
                (piece.name, piece.source_start, piece.source_end, piece.output_start)
                for piece in AUDIO_PIECES
            ],
            [
                ("sale", 176.80, 179.38, 0.00),
                ("equity", 182.16, 190.94, 2.58),
                ("finance", 198.00, 203.86, 11.36),
                ("revenue", 18.82, 22.48, 17.22),
                ("profit_context", 398.30, 402.42, 20.88),
                ("owner_pay", 438.56, 443.58, 25.00),
                ("hours", 235.76, 244.08, 30.02),
                ("systems", 249.00, 260.26, 38.34),
            ],
        )
        self.assertAlmostEqual(
            AUDIO_PIECES[-1].output_start + AUDIO_PIECES[-1].duration,
            49.60,
        )

    def test_user_reported_silent_windows_are_covered_by_source_dialogue(self):
        ranges = [
            (piece.output_start, piece.output_start + piece.duration)
            for piece in AUDIO_PIECES
        ]
        for timestamp in (21.00, 23.50, 44.00, 49.50):
            self.assertTrue(
                any(start <= timestamp < end for start, end in ranges),
                f"no source dialogue at {timestamp:.2f}s",
            )

    def test_hook_uses_moving_stock_instead_of_freeze_frames(self):
        self.assertEqual(
            [(clip.name, clip.frames) for clip in TIMELINE[:3]],
            [("hook_face_a", 24), ("hook_face_b", 27), ("hook_face_c", 33)],
        )
        self.assertEqual(
            [VISUAL_RECIPES[name].kind for name in ("hook_face_a", "hook_face_b", "hook_face_c")],
            ["pexels", "pexels", "pexels"],
        )
        self.assertEqual(
            [VISUAL_RECIPES[name].pexels_key for name in ("hook_face_a", "hook_face_b", "hook_face_c")],
            ["hook_owner", "hook_owner", "hook_money"],
        )
        self.assertEqual(
            [VISUAL_RECIPES[name].pexels_start for name in ("hook_face_a", "hook_face_b", "hook_face_c")],
            [0.00, 0.80, 0.00],
        )
        self.assertEqual([clip.is_source_footage for clip in TIMELINE[:3]], [False] * 3)

    def test_production_timeline_passes_transformative_gate(self):
        validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
        self.assertEqual(source_share(TIMELINE), 0.444)

    def test_financial_summary_uses_grounded_numbers(self):
        values = financial_summary(Financials())
        self.assertEqual(values["purchase_price"], 300_000)
        self.assertEqual(values["cash_at_risk"], 200_000)
        self.assertEqual(values["profit"], 119_000)
        self.assertEqual(values["owner_pay"], 66_000)
        self.assertAlmostEqual(values["profit_margin"], 119_000 / 475_000)

    def test_source_share_is_frame_accurate(self):
        clips = [
            TimelineClip("source", 0, 300, True),
            TimelineClip("pexels", 300, 900, False),
            TimelineClip("source", 900, 1200, True),
            TimelineClip("pexels", 1200, 1500, False),
        ]
        self.assertEqual(source_share(clips), 0.4)

    def test_timeline_rejects_source_share_above_half(self):
        clips = [
            TimelineClip("source_a", 0, 400, True),
            TimelineClip("pexels_a", 400, 500, False),
            TimelineClip("source_b", 500, 900, True),
            TimelineClip("pexels_b", 900, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "source share"):
            validate_timeline(clips, total_frames=1500)

    def test_timeline_rejects_gaps(self):
        clips = [
            TimelineClip("a", 0, 300, True),
            TimelineClip("b", 301, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "gap or overlap"):
            validate_timeline(clips, total_frames=1500)

    def test_timeline_rejects_source_clip_at_or_above_15_seconds(self):
        clips = [
            TimelineClip("source", 0, 450, True),
            TimelineClip("pexels", 450, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "15 seconds"):
            validate_timeline(clips, total_frames=1500)


if __name__ == "__main__":
    unittest.main()
