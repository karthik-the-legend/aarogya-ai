import sys
sys.path.insert(0, 'backend')
from voice_handler import transcribe

tests = [
    ("test_hindi.mp3",   "hi", "Hindi"),
    ("test_telugu.mp3",  "te", "Telugu"),
    ("test_tamil.mp3",   "ta", "Tamil"),
]

for filename, expected_lang, lang_name in tests:
    print(f"\n--- {lang_name} Transcription ---")
    result = transcribe(filename)
    print(f"Text     : {result['text']}")
    print(f"Lang Code: {result['lang_code']}")
    print(f"Duration : {result['duration']}s")
    status = "PASSED" if result['lang_code'] == expected_lang else f"CHECK — got {result['lang_code']}"
    print(f"STATUS   : {status}")

print("\nAll transcription tests complete!")