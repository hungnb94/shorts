import unittest

from render_laundromat_v1 import (
    AUDIO_PIECES,
    Financials,
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
    def test_music_is_audible_during_visual_only_profit_checkpoint(self):
        self.assertEqual(
            music_volume_expression(),
            "volume='if(between(t,20.88,25.00),0.20,if(gte(t,43.02),0.22,0.035))':eval=frame",
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
                ("owner_pay", 438.56, 443.58, 25.00),
                ("hours", 235.76, 244.08, 30.02),
                ("systems", 249.00, 253.68, 38.34),
            ],
        )
        self.assertAlmostEqual(
            AUDIO_PIECES[-1].output_start + AUDIO_PIECES[-1].duration,
            43.02,
        )

    def test_hook_uses_clean_action_windows_not_graphic_windows(self):
        self.assertEqual(
            [(clip.name, clip.frames) for clip in TIMELINE[:3]],
            [("hook_face_a", 24), ("hook_face_b", 27), ("hook_face_c", 33)],
        )
        self.assertEqual(
            [VISUAL_RECIPES[name].kind for name in ("hook_face_a", "hook_face_b", "hook_face_c")],
            ["freeze", "freeze", "freeze"],
        )
        self.assertEqual(
            [VISUAL_RECIPES[name].source_start for name in ("hook_face_a", "hook_face_b", "hook_face_c")],
            [236.08, 240.00, 244.00],
        )
        first_ten = [
            VISUAL_RECIPES[name].source_start
            for name in (
                "hook_face_a",
                "hook_face_b",
                "hook_face_c",
                "bet_owner",
                "bet_house_split",
                "price_contract_split",
            )
        ]
        self.assertNotIn(18.08, first_ten)
        self.assertNotIn(438.80, first_ten)

    def test_production_timeline_passes_transformative_gate(self):
        validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
        self.assertEqual(source_share(TIMELINE), 0.5)

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
