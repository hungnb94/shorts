import unittest

from pipeline.trademe.render_trademe_v1 import (
    EDGE_TTS_VOICE,
    MAX_POST_TEMPO,
    compute_fit_tempo,
    tts_lines,
)


class TTSEnergyPolicyTest(unittest.TestCase):
    def test_uses_positive_confident_neural_voice(self) -> None:
        self.assertEqual(EDGE_TTS_VOICE, "en-US-AriaNeural")

    def test_every_beat_has_explicit_prosody_direction(self) -> None:
        lines = tts_lines()
        self.assertEqual(
            [line.name for line in lines],
            ["hook", "criticism", "start", "ladder", "swap", "buyer", "value", "house", "insight"],
        )
        self.assertEqual(
            [(line.rate_percent, line.pitch_hz) for line in lines],
            [(8, 3), (14, 2), (10, 4), (14, 3), (12, 2), (8, 4), (9, 1), (12, 3), (4, 0)],
        )
        self.assertTrue(all(line.synthesis_text for line in lines))

    def test_short_line_is_never_slowed(self) -> None:
        self.assertEqual(compute_fit_tempo(raw_duration=2.0, target_duration=4.0), 1.0)

    def test_overlong_line_uses_only_bounded_speedup(self) -> None:
        tempo = compute_fit_tempo(raw_duration=3.7, target_duration=3.5)
        self.assertGreater(tempo, 1.0)
        self.assertLessEqual(tempo, MAX_POST_TEMPO)

    def test_impossible_fit_is_rejected_instead_of_truncated(self) -> None:
        with self.assertRaisesRegex(ValueError, "timing budget"):
            compute_fit_tempo(raw_duration=4.2, target_duration=3.5)


if __name__ == "__main__":
    unittest.main()
