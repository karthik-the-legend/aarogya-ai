import sys
sys.path.insert(0, 'backend')
from triage import classify

print("Testing language detection in emergency messages\n")

tests = [
    ("सीने में दर्द है",   "Hindi"),
    ("மார்பு வலி",         "Tamil"),
    ("ఛాతీ నొప్పి",        "Telugu"),
    ("ಎದೆ ನೋವು",           "Kannada"),
    ("I have chest pain",  "English"),
]

for query, lang in tests:
    result = classify(query)
    print(f"Language : {lang}")
    print(f"Query    : {query}")
    print(f"Level    : {result.level.value}")
    print(f"Message  : {result.message}")
    print(f"Triggered: {result.triggered}")
    print()

print("Language detection test complete!")