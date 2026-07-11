import subprocess, sys, json
from pathlib import Path
import mlx_whisper

text = sys.argv[1] if len(sys.argv) > 1 else "Straight from Anthropic's own stage."
out_wav = sys.argv[2] if len(sys.argv) > 2 else "output/projects/aiwork/source/commentary_v1.wav"
voice = sys.argv[3] if len(sys.argv) > 3 else "Samantha"
rate = sys.argv[4] if len(sys.argv) > 4 else "175"

raw = str(Path(out_wav).with_suffix(".raw.wav"))
subprocess.run(["say", "-v", voice, "-r", rate, "-o", raw, "--data-format=LEF32@48000", text], check=True)
# say outputs mono; re-encode to 48kHz stereo WAV to match the source segment's audio format.
subprocess.run(["ffmpeg", "-y", "-i", raw, "-ar", "48000", "-ac", "2", out_wav], check=True)
Path(raw).unlink()
print(f"[tts] wrote {out_wav}")

out_json = out_wav.rsplit(".", 1)[0] + "_transcript.json"
result = mlx_whisper.transcribe(
    out_wav,
    path_or_hf_repo="mlx-community/whisper-medium-mlx",
    language="en",
    word_timestamps=True,
)
with open(out_json, "w") as f:
    json.dump(result, f, indent=2)
print(f"[tts] transcribed -> {out_json}")
