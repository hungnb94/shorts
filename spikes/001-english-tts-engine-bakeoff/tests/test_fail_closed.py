#!/usr/bin/env python3
import importlib.util
import json
import math
import struct
import sys
import tempfile
import types
import unittest
import wave
from pathlib import Path

SPIKE = Path(__file__).resolve().parents[1]
SCRIPTS = SPIKE / "scripts"
sys.path.insert(0, str(SCRIPTS))
PROFILE = json.loads(
    (SPIKE.parents[1] / "data" / "narrator-voices" / "natural_talker_male_qwen_blog" / "profile.json").read_text()
)
CORPUS = json.loads((SPIKE / "corpus.json").read_text())["samples"]

from runtime_provenance import locked_packages


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_wav(path: Path, duration: float, frequency: float) -> None:
    sample_rate = 24_000
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        frames = (
            struct.pack("<h", int(4_000 * math.sin(2 * math.pi * frequency * index / sample_rate)))
            for index in range(int(duration * sample_rate))
        )
        output.writeframes(b"".join(frames))


class FailClosedRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work = Path(self.temp_dir.name)
        synthesis = PROFILE["runtime"]["environments"]["synthesis"]
        runtime_environment = {
            "name": "synthesis",
            "python": synthesis["python"],
            "python_implementation": "cpython",
            "lock_file": synthesis["lock_file"],
            "lock_sha256": synthesis["lock_sha256"],
            "packages": dict(
                sorted(locked_packages(SPIKE / synthesis["lock_file"]).items())
            ),
        }
        clone = PROFILE["models"]["voice_clone"]
        model_resolution = {
            "repo_id": clone["repo_id"],
            "requested_revision": clone["revision"],
            "resolved_revision": clone["revision"],
            "local_snapshot": str(self.work / "fake-snapshot"),
            "weights": clone["weights"],
        }
        durations = {"hook": 2.0, "finance": 9.0, "ai": 9.0, "stress": 6.0}
        for run_id in ("run_a", "run_b"):
            records = []
            for sample in CORPUS:
                output = Path("raw") / run_id / f"{sample['id']}.wav"
                frequency = 440.0 + (30.0 if run_id == "run_b" and sample["id"] == "hook" else 0.0)
                write_wav(self.work / output, durations[sample["id"]], frequency)
                records.append(
                    {
                        "sample_id": sample["id"],
                        "run_id": run_id,
                        "source_text": sample["text"],
                        "output": str(output),
                        "sample_rate": 24_000,
                        "duration_seconds": durations[sample["id"]],
                        "synthesis_seconds": 0.1,
                        "sha256": self._sha256(self.work / output),
                    }
                )
            generation = {
                "run_id": run_id,
                "profile_id": PROFILE["id"],
                "strategy": PROFILE["runtime"]["strategy"],
                "model": PROFILE["models"]["voice_clone"],
                "model_resolution": model_resolution,
                "runtime_environment": runtime_environment,
                "system_fingerprints": PROFILE["runtime"]["repeatability_fingerprints"],
                "seed_policy": f"{PROFILE['generation']['seed']} + stable corpus index; reset before each item",
                "settings": PROFILE["generation"]["clone"],
                "reference_sha256": PROFILE["identity"]["reference_sha256"],
                "records": records,
            }
            (self.work / f"generation_{run_id}.json").write_text(json.dumps(generation))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _sha256(path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_prepare_rejects_unequal_cross_process_hashes(self) -> None:
        prepare = load_script("prepare_repeatability")
        prepare.WORK = self.work
        with self.assertRaises(SystemExit) as raised:
            prepare.main()
        self.assertNotEqual(raised.exception.code, 0)
        manifest = json.loads((self.work / "repeatability_manifest.json").read_text())
        self.assertFalse(manifest["all_checks_passed"])
        self.assertTrue(any("raw hash mismatch" in failure for failure in manifest["failures"]))

    def test_asr_refuses_failed_prepare_manifest_before_transcription(self) -> None:
        (self.work / "repeatability_manifest.json").write_text(
            json.dumps(
                {
                    "profile_id": PROFILE["id"],
                    "all_checks_passed": False,
                    "failures": ["controlled mismatch"],
                    "cross_process_comparisons": [
                        {"sample_id": sample["id"], "raw_hash_equal": False, "normalized_hash_equal": False}
                        for sample in CORPUS
                    ],
                    "auditions": [],
                }
            )
        )
        fake_whisper = types.SimpleNamespace(
            transcribe=lambda *args, **kwargs: self.fail("ASR must not run for a failed manifest")
        )
        sys.modules["mlx_whisper"] = fake_whisper
        try:
            asr = load_script("asr_repeatability")
            asr.WORK = self.work
            with self.assertRaisesRegex(RuntimeError, "all_checks_passed|comparison"):
                asr.main()
        finally:
            sys.modules.pop("mlx_whisper", None)

    def test_lcs_word_recall_preserves_order_and_multiplicity(self) -> None:
        asr = load_script("asr_repeatability")
        self.assertEqual(
            asr.lcs_word_recall(
                ["the", "cat", "the", "cat"],
                ["the", "cat"],
            ),
            0.5,
        )


if __name__ == "__main__":
    unittest.main()
