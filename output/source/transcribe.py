import json, time, sys
import mlx_whisper

start_time = time.time()
result = mlx_whisper.transcribe(
    'audio_16k.wav',
    path_or_hf_repo='mlx-community/whisper-small-mlx',
    language='en',
    word_timestamps=True,
)
elapsed = time.time() - start_time
print(f'Transcription took {elapsed:.1f}s')

with open('../transcript_full.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f'Segments: {len(result["segments"])}')
print('DONE')
