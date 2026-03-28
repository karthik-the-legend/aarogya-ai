import sys
import json
import requests
sys.path.insert(0, 'backend')

BASE_URL = "http://localhost:8000"

queries = [
    ("en", "What are symptoms of dengue fever?"),
    ("hi", "मुझे बुखार है"),
    ("en", "How is malaria treated?"),
    ("ta", "எனக்கு காய்ச்சல்"),
    ("en", "What causes typhoid?"),
    ("te", "నాకు జ్వరం"),
    ("en", "Is TB contagious?"),
    ("hi", "डेंगू के लक्षण क्या हैं"),
    ("en", "How to stop diarrhoea?"),
    ("kn", "ನನಗೆ ಜ್ವರ"),
    ("en", "What medicine for high fever?"),
    ("hi", "मलेरिया का इलाज"),
    ("en", "How long does cholera last?"),
    ("ta", "மலேரியா என்றால் என்ன"),
    ("en", "Can flu be treated with antibiotics?"),
    ("te", "టైఫాయిడ్ లక్షణాలు"),
    ("en", "What causes skin infections?"),
    ("hi", "खांसी का इलाज"),
    ("en", "Signs of cholera?"),
    ("en", "Dengue drug warning ibuprofen"),
]

print("Running 20 latency tests...")
latencies = []

for i, (lang, query) in enumerate(queries, 1):
    r = requests.post(f"{BASE_URL}/ask", json={
        "query"        : query,
        "lang_code"    : lang,
        "language_name": "English"
    })
    ms = r.json().get('latency_ms', 0)
    latencies.append(ms)
    print(f"  {i:2}. {query[:40]:<40} → {ms}ms")

# Calculate stats
avg_ms = sum(latencies) // len(latencies)
min_ms = min(latencies)
max_ms = max(latencies)

print(f"\n  Average : {avg_ms}ms")
print(f"  Min     : {min_ms}ms")
print(f"  Max     : {max_ms}ms")

# Save to logs
log = {
    "latencies" : latencies,
    "average_ms": avg_ms,
    "min_ms"    : min_ms,
    "max_ms"    : max_ms,
    "queries"   : [q for _, q in queries]
}
with open("logs/latency_log.json", "w") as f:
    json.dump(log, f, indent=2)

print("\n  Saved to logs/latency_log.json")