import sys, traceback, os
sys.path.insert(0, '.')

video_path = r'uploads\178a6539-fafa-4183-8b56-fee4708cc30c\videoplayback (1).mp4'

print('=== STEP 1: extract_audio ===')
try:
    from video_utils import extract_audio
    extract_audio(video_path, 'test_audio.wav')
    print('extract_audio OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)

print('=== STEP 2: faster-whisper transcribe ===')
try:
    from models import get_whisper
    model_wh = get_whisper()
    result = model_wh.transcribe('test_audio.wav', language='en', word_timestamps=False)
    segs = result.get('segments', [])
    print(f'Transcription OK - {len(segs)} segments')
    print('First 100 chars:', result["text"][:100])
except Exception:
    traceback.print_exc()
    sys.exit(1)

print('=== ALL OK ===')
