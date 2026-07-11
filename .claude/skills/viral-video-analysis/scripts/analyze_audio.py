#!/usr/bin/env python3
"""
analyze_audio.py - sound-design analysis via librosa onset/beat/energy detection.

New capability (no prior tool in this repo did automated audio-event analysis
-- pipeline/tools/*.py only transcribe speech-to-text). This script answers a
different question than transcription: WHERE do beats, percussive hits,
and loudness jumps land in time, independent of spoken words. That is the raw
signal needed to judge sound design (whoosh/riser/impact, "cut on the beat")
without a human re-listening frame-by-frame.

Pipeline:
  1. ffmpeg extracts the audio track to a temp mono WAV (matches the 16kHz
     convention already used by pipeline/tools/transcribe.py).
  2. librosa loads it and computes:
     - tempo estimate + beat timestamps (librosa.beat.beat_track)
     - onset timestamps (librosa.onset.onset_detect) - percussive/attack events,
       candidates for sound-effect hits (whoosh/riser/impact) or cut points
     - an RMS energy envelope, from which "energy jumps" (loudness deltas above
       a threshold) are extracted as a proxy for music swells/drops
  3. If --cut-timestamps is given (comma-separated seconds, e.g. copied from
     extract_keyframes.py's manifest.json scene_keyframes), each cut is
     checked against the nearest onset/beat within +/-150ms to flag whether
     the edit is "cut on the beat" - a concrete, checkable sound-design
     pattern rather than a guess.

Usage:
    python3 analyze_audio.py <video_or_audio_path> [--cut-timestamps 0.0,1.2,3.4] \
        [--output report.json]

Dependencies: librosa, ffmpeg (system). Installed in this repo's .venv.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def check_dependencies():
    missing = []
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        missing.append("ffmpeg (install: brew install ffmpeg)")
    try:
        import librosa  # noqa: F401
    except ImportError:
        missing.append("librosa (install: pip install librosa)")
    if missing:
        print("ERROR: Missing dependencies:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)


def extract_audio(src_path: str, out_wav: str, sample_rate: int = 16000):
    cmd = [
        "ffmpeg", "-y", "-i", src_path,
        "-vn", "-ac", "1", "-ar", str(sample_rate),
        out_wav,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg audio extraction failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def analyze(wav_path: str, energy_jump_threshold_db: float = 6.0) -> dict:
    import librosa
    import numpy as np

    y, sr = librosa.load(wav_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).round(2).tolist()
    tempo_bpm = round(float(np.asarray(tempo).reshape(-1)[0]), 1)

    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).round(2).tolist()

    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    energy_jumps = []
    for i in range(1, len(rms_db)):
        delta = float(rms_db[i] - rms_db[i - 1])
        if delta >= energy_jump_threshold_db:
            energy_jumps.append({
                "time": round(float(rms_times[i]), 2),
                "delta_db": round(delta, 1),
            })

    return {
        "duration_sec": round(float(duration), 2),
        "tempo_bpm": tempo_bpm,
        "beat_times": beat_times,
        "onset_times": onset_times,
        "energy_jumps": energy_jumps,
    }


def align_cuts(cut_timestamps: list, onset_times: list, beat_times: list, window: float = 0.15) -> list:
    events = sorted(onset_times + beat_times)
    aligned = []
    for cut in cut_timestamps:
        nearest = min(events, key=lambda t: abs(t - cut)) if events else None
        on_beat = nearest is not None and abs(nearest - cut) <= window
        aligned.append({
            "cut_time": cut,
            "nearest_audio_event": nearest,
            "delta_sec": round(abs(nearest - cut), 3) if nearest is not None else None,
            "cut_on_beat": on_beat,
        })
    return aligned


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("media_path", help="path to video or audio file")
    parser.add_argument("--cut-timestamps", help="comma-separated seconds to check against detected onsets/beats")
    parser.add_argument("--energy-jump-db", type=float, default=6.0, help="min dB jump to flag as an energy jump (default 6.0)")
    parser.add_argument("--output", "-o", help="write JSON report to file")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    check_dependencies()

    media_path = Path(args.media_path)
    if not media_path.exists():
        print(f"ERROR: File not found: {media_path}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory(prefix="vva_audio_") as tmpdir:
        wav_path = str(Path(tmpdir) / "audio_16k.wav")
        if args.verbose:
            print(f"[INFO] Extracting audio -> {wav_path}", file=sys.stderr)
        extract_audio(str(media_path), wav_path)

        if args.verbose:
            print("[INFO] Running librosa onset/beat/energy analysis...", file=sys.stderr)
        report = analyze(wav_path, energy_jump_threshold_db=args.energy_jump_db)

    if args.cut_timestamps:
        cuts = [float(t) for t in args.cut_timestamps.split(",") if t.strip()]
        report["cuts_aligned_with_audio"] = align_cuts(cuts, report["onset_times"], report["beat_times"])

    report["media"] = media_path.name

    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        if args.verbose:
            print(f"[INFO] Report written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
