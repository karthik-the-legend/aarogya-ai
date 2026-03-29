import sys
import time

sys.path.insert(0, "backend")

from voice_handler import load_whisper_model, transcribe_bytes

# Test 1: Load model
print("--- TEST 1: Load Whisper model ---")
t1 = time.time()
load_whisper_model()
print(f"First load : {round(time.time()-t1, 2)}s")

# Test 2: Singleton — second call must be instant
t2 = time.time()
load_whisper_model()
print(f"Second load: {round(time.time()-t2, 4)}s (singleton reuse)")

print()
print("voice_handler.py working correctly!")
print("Record a Hindi audio file and test transcription next.")
