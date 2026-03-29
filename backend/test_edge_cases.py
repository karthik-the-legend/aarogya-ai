import sys
import requests

sys.path.insert(0, "backend")

BASE_URL = "http://localhost:8000"

print("=" * 55)
print("  Edge Case Tests")
print("=" * 55)

# Test 1: Empty query — must return 422
print("\nTest 1: Empty query")
r = requests.post(
    f"{BASE_URL}/ask", json={"query": "", "lang_code": "en", "language_name": "English"}
)
print(f"  Status: {r.status_code} (expected 422)")
print(f"  PASSED" if r.status_code == 422 else f"  FAILED — got {r.status_code}")

# Test 2: Very long query
print("\nTest 2: Long query (500 chars)")
long_query = "I have fever and headache. " * 20
r = requests.post(
    f"{BASE_URL}/ask",
    json={"query": long_query[:500], "lang_code": "en", "language_name": "English"},
)
print(f"  Status : {r.status_code}")
print(f"  Latency: {r.json().get('latency_ms')}ms")
print(f"  PASSED" if r.status_code == 200 else "  FAILED")

# Test 3: Gibberish
print("\nTest 3: Gibberish query")
r = requests.post(
    f"{BASE_URL}/ask",
    json={"query": "xyzabc123!!!???", "lang_code": "en", "language_name": "English"},
)
ans = r.json().get("answer", "")
print(f"  Status : {r.status_code}")
print(f"  Answer : {ans[:150]}")
print(f"  PASSED" if r.status_code == 200 else "  FAILED")

# Test 4: RED triage override
print("\nTest 4: RED triage override")
r = requests.post(
    f"{BASE_URL}/ask",
    json={
        "query": "I have chest pain and can't breathe",
        "lang_code": "en",
        "language_name": "English",
    },
)
data = r.json()
print(f"  Triage  : {data['triage_level']}")
print(f"  Override: {data['triage_override']}")
print(f"  Answer  : {data['answer'][:100]}")
print(f"  PASSED" if data["triage_level"] == "red" else "  FAILED — not RED")

# Test 5: Unknown language code
print("\nTest 5: Unknown language code")
r = requests.post(
    f"{BASE_URL}/ask",
    json={"query": "I have fever", "lang_code": "xx", "language_name": "Unknown"},
)
print(f"  Status : {r.status_code}")
print(f"  PASSED — no crash" if r.status_code == 200 else f"  Status {r.status_code}")

print("\n" + "=" * 55)
print("  All edge case tests complete!")
print("=" * 55)
