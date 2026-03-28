import sys
import requests
sys.path.insert(0, 'backend')

BASE_URL = "http://localhost:8000"

tests = [
    ("Hindi",   "hi", "मुझे बुखार है"),
    ("Tamil",   "ta", "எனக்கு காய்ச்சல் இருக்கிறது"),
    ("Telugu",  "te", "నాకు జ్వరం వచ్చింది"),
    ("Kannada", "kn", "ನನಗೆ ಜ್ವರ ಬಂದಿದೆ"),
]

print("=" * 55)
print("  4 Language Tests")
print("=" * 55)

for lang, code, query in tests:
    r = requests.post(f"{BASE_URL}/ask", json={
        "query"        : query,
        "lang_code"    : code,
        "language_name": lang
    })
    data = r.json()
    print(f"\n  {lang}:")
    print(f"  Query   : {query}")
    print(f"  Answer  : {data['answer'][:150]}")
    print(f"  Triage  : {data['triage_level']}")
    print(f"  Sources : {len(data['sources'])} chunks")
    print(f"  Latency : {data['latency_ms']}ms")
    ok = len(data['sources']) > 0
    print(f"  STATUS  : {'PASSED' if ok else 'FAILED — no sources'}")

print("\n" + "=" * 55)
print("  All language tests complete!")
print("=" * 55)