#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
from pathlib import Path

SPIKE = Path(__file__).resolve().parents[1]
REPO = SPIKE.parents[1]
PROFILE_DIR = REPO / "data" / "narrator-voices" / "natural_talker_male_qwen_blog"
PROFILE_PATH = PROFILE_DIR / "profile.json"
EXPECTED_PROFILE_ID = "natural_talker_male_qwen_blog"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_reference(profile: dict) -> Path:
    if profile.get("id") != EXPECTED_PROFILE_ID:
        raise RuntimeError(f"Unexpected profile ID: {profile.get('id')}")
    value = profile["identity"].get("reference_audio")
    if not isinstance(value, str):
        raise RuntimeError("reference_audio must be a relative filename")
    relative = Path(value)
    if relative.is_absolute() or len(relative.parts) != 1 or relative.name != value:
        raise RuntimeError(f"Unsafe reference_audio path: {value}")
    audio = (PROFILE_DIR / relative).resolve()
    if audio.parent != PROFILE_DIR.resolve():
        raise RuntimeError(f"reference_audio escapes canonical profile directory: {value}")
    return audio


def verify_provenance(profile: dict) -> None:
    for name in ("voice_design", "voice_clone"):
        model = profile["models"][name]
        revision = model.get("revision", "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise RuntimeError(f"{name} has no immutable revision")
        if model.get("license") != "Apache-2.0" or revision not in model.get("license_url", ""):
            raise RuntimeError(f"{name} license evidence is not revision-pinned")
        for weight in model.get("weights", []):
            relative = Path(weight.get("path", ""))
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe {name} weight path: {relative}")
            if not re.fullmatch(r"[0-9a-f]{64}", weight.get("sha256", "")):
                raise RuntimeError(f"{name}/{relative} has no SHA-256")
            if not isinstance(weight.get("size_bytes"), int) or weight["size_bytes"] <= 0:
                raise RuntimeError(f"{name}/{relative} has invalid size")

    for environment in profile["runtime"]["environments"].values():
        lock_name = environment["lock_file"]
        if Path(lock_name).name != lock_name:
            raise RuntimeError(f"Unsafe lock path: {lock_name}")
        lock = SPIKE / lock_name
        if sha256(lock) != environment["lock_sha256"]:
            raise RuntimeError(f"Lock SHA-256 mismatch: {lock_name}")


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text())
    verify_provenance(profile)
    identity = profile["identity"]
    audio = canonical_reference(profile)
    if not audio.is_file():
        raise RuntimeError(f"Missing canonical reference: {audio}")
    actual_hash = sha256(audio)
    if actual_hash != identity["reference_sha256"]:
        raise RuntimeError(f"Reference hash mismatch: {actual_hash}")
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,sample_rate,channels",
            "-of", "json", str(audio),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    probe = json.loads(result.stdout)
    stream = probe["streams"][0]
    expected = identity["reference_format"]
    checks = {
        "canonical_status": profile["status"] == "canonical",
        "finance_assignment": profile["assignment"] == {
            "destination_channel": "finance",
            "language": "en",
            "role": "synthetic_narrator",
        },
        "sha256": actual_hash == identity["reference_sha256"],
        "codec": stream["codec_name"] == expected["codec"],
        "sample_rate": int(stream["sample_rate"]) == expected["sample_rate"],
        "channels": stream["channels"] == expected["channels"],
        "duration": abs(float(probe["format"]["duration"]) - expected["duration_seconds"]) < 0.001,
        "synthetic_origin": profile["provenance"]["type"] == "locally_generated_synthetic_voice",
        "runtime_activation_deferred": profile["runtime_activation"]["status"] == "pending_integration",
    }
    if not all(checks.values()):
        raise RuntimeError(f"Profile verification failed: {checks}")
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "null", "-"], check=True)
    print(json.dumps({"profile": profile["id"], "reference": str(audio), "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
