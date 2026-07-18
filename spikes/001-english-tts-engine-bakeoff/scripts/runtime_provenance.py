#!/usr/bin/env python3
import hashlib
import importlib.metadata
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PACKAGE_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^ ;\\]+)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def locked_packages(lock_path: Path) -> dict[str, str]:
    packages: dict[str, str] = {}
    for line in lock_path.read_text().splitlines():
        match = PACKAGE_PATTERN.match(line)
        if match:
            packages[normalized_package_name(match.group(1))] = match.group(2)
    if not packages:
        raise RuntimeError(f"No exact package pins found in {lock_path}")
    return packages


def verify_environment(profile: dict[str, Any], spike: Path, environment_name: str) -> dict[str, Any]:
    expected = profile["runtime"]["environments"][environment_name]
    actual_python = platform.python_version()
    if actual_python != expected["python"]:
        raise RuntimeError(f"Python {actual_python} does not match pinned {expected['python']}")
    lock_path = spike / expected["lock_file"]
    actual_lock_sha = sha256(lock_path)
    if actual_lock_sha != expected["lock_sha256"]:
        raise RuntimeError(f"Lock SHA-256 mismatch for {lock_path.name}: {actual_lock_sha}")
    expected_packages = locked_packages(lock_path)
    installed_packages = {
        normalized_package_name(distribution.metadata["Name"]): distribution.version
        for distribution in importlib.metadata.distributions()
        if distribution.metadata.get("Name")
    }
    mismatches = {
        name: {"expected": version, "installed": installed_packages.get(name)}
        for name, version in expected_packages.items()
        if installed_packages.get(name) != version
    }
    if mismatches:
        raise RuntimeError(f"Installed packages do not match {lock_path.name}: {mismatches}")
    return {
        "name": environment_name,
        "python": actual_python,
        "python_implementation": sys.implementation.name,
        "lock_file": expected["lock_file"],
        "lock_sha256": actual_lock_sha,
        "packages": dict(sorted(expected_packages.items())),
    }


def _command_stdout(command: list[str]) -> bytes:
    return subprocess.run(command, check=True, capture_output=True).stdout


def system_fingerprints() -> dict[str, Any]:
    ffmpeg_output = _command_stdout(["ffmpeg", "-version"])
    return {
        "ffmpeg": {
            "version_line": ffmpeg_output.decode().splitlines()[0],
            "version_output_sha256": hashlib.sha256(ffmpeg_output).hexdigest(),
        },
        "platform": {
            "system": platform.system(),
            "macos_version": _command_stdout(["sw_vers", "-productVersion"]).decode().strip(),
            "macos_build": _command_stdout(["sw_vers", "-buildVersion"]).decode().strip(),
            "machine": platform.machine(),
        },
    }


def verify_system_fingerprints(profile: dict[str, Any]) -> dict[str, Any]:
    actual = system_fingerprints()
    expected = profile["runtime"]["repeatability_fingerprints"]
    if actual != expected:
        raise RuntimeError(f"System fingerprint mismatch: expected {expected}, got {actual}")
    return actual


def verified_model_snapshot(model_spec: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    from huggingface_hub import snapshot_download

    revision = model_spec["revision"]
    snapshot = Path(
        snapshot_download(repo_id=model_spec["repo_id"], revision=revision)
    ).absolute()
    resolved_revision = snapshot.resolve().name
    if resolved_revision != revision:
        raise RuntimeError(
            f"Resolved model revision {resolved_revision} does not match pinned {revision}"
        )
    verified_weights = []
    for expected in model_spec["weights"]:
        relative = Path(expected["path"])
        if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != expected["path"]:
            raise RuntimeError(f"Unsafe model weight path: {expected['path']}")
        weight = snapshot / relative
        if not weight.is_file():
            raise RuntimeError(f"Missing model weight: {weight}")
        actual_size = weight.stat().st_size
        actual_sha = sha256(weight)
        if actual_size != expected["size_bytes"] or actual_sha != expected["sha256"]:
            raise RuntimeError(
                f"Model weight mismatch for {expected['path']}: "
                f"size={actual_size}, sha256={actual_sha}"
            )
        verified_weights.append(
            {"path": expected["path"], "size_bytes": actual_size, "sha256": actual_sha}
        )
    evidence = {
        "repo_id": model_spec["repo_id"],
        "requested_revision": revision,
        "resolved_revision": resolved_revision,
        "local_snapshot": str(snapshot),
        "weights": verified_weights,
    }
    return snapshot, evidence
