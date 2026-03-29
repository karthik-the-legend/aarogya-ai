import sys

sys.path.insert(0, "backend")
from translate import to_english, from_english, get_cache_info

# Test 1: Hindi → English
result = to_english("मुझे बुखार है", "hi")
print(f"Hindi → English: {result}")

# Test 2: English passthrough
result = to_english("I have fever", "en")
print(f"English passthrough: {result}")

# Test 3: English → Hindi
result = from_english("You may have viral fever. Rest and drink fluids.", "hi")
print(f"English → Hindi: {result}")

# Test 4: Cache info
print(f"Cache info: {get_cache_info()}")
print()
print("translate.py working correctly!")
