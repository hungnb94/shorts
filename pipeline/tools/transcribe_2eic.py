import mlx_whisper, json, sys

audio = "output/source/2eic_audio.wav"
model = sys.argv[1] if len(sys.argv) > 1 else "mlx-community/whisper-medium-mlx"
out = sys.argv[2] if len(sys.argv) > 2 else "output/source/2eic_transcript.json"

print(f"[whisper] model={model} audio={audio}", flush=True)
result = mlx_whisper.transcribe(
    audio,
    path_or_hf_repo=model,
    language="en",
    word_timestamps=True,
)
with open(out, "w") as f:
    json.dump(result, f, indent=2)
segs = result.get("segments", [])
print(f"[whisper] DONE: {len(segs)} segments -> {out}", flush=True)
