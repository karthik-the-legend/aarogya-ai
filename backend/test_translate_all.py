import sys
sys.path.insert(0, 'backend')
from translate import to_english, from_english

queries = [
    ("मुझे बुखार है और सिरदर्द है",  "hi", "Hindi"),
    ("எனக்கு காய்ச்சல் இருக்கிறது",   "ta", "Tamil"),
    ("నాకు జ్వరం వచ్చింది",            "te", "Telugu"),
    ("ನನಗೆ ಜ್ವರ ಬಂದಿದೆ",              "kn", "Kannada"),
]

print("Testing all Indian languages → English\n")
all_passed = True

for text, code, name in queries:
    result = to_english(text, code)
    status = "PASSED" if "fever" in result.lower() else "CHECK"
    if status == "CHECK":
        all_passed = False
    print(f"  {name:10} | {text[:25]} → {result}")
    print(f"             Status: {status}\n")

# Test English → Hindi (response translation)
print("Testing English → Hindi (response translation)")
english = "Drink plenty of fluids and rest. See a doctor if fever exceeds 103F."
hindi   = from_english(english, "hi")
print(f"  English: {english}")
print(f"  Hindi  : {hindi}")

print()
print("All languages tested!" if all_passed else "Some results need checking.")