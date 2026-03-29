import sys

sys.path.insert(0, "backend")

from translate import to_english, get_cache_info
import time

print("Testing LRU Cache Performance\n")

# ── First call (CACHE MISS — hits Google Translate) ──
t1 = time.time()
r1 = to_english("मुझे बुखार है", "hi")
t1 = round((time.time() - t1) * 1000)
print(f"CALL 1 (cache MISS): {t1}ms → {r1}")

# ── Second call (same input — CACHE HIT) ─────────────
t2 = time.time()
r2 = to_english("मुझे बुखार है", "hi")
t2 = round((time.time() - t2) * 1000)
print(f"CALL 2 (cache HIT):  {t2}ms → {r2}")

# ── Third call (different input — CACHE MISS) ─────────
t3 = time.time()
r3 = to_english("मुझे सिरदर्द है", "hi")
t3 = round((time.time() - t3) * 1000)
print(f"CALL 3 (new query):  {t3}ms → {r3}")

# ── Fourth call (same as call 1 — CACHE HIT) ──────────
t4 = time.time()
r4 = to_english("मुझे बुखार है", "hi")
t4 = round((time.time() - t4) * 1000)
print(f"CALL 4 (cache HIT):  {t4}ms → {r4}")

# ── Cache stats ────────────────────────────────────────
info = get_cache_info()
ci = info["to_english"]
print(f'\nCache info: hits={ci["hits"]}, misses={ci["misses"]}')
print(f'            size={ci["currsize"]}/{ci["maxsize"]}')

# ── Summary ────────────────────────────────────────────
print(f"\nSpeedup: cache hit is {round(t1/max(t2,1))}x faster than miss")
print("Cache test complete!")
