# Fix two failing Kannada keywords using exact Unicode codepoints

# ಉಸಿರಾಡಲು ಕಷ್ಟ ಆಗುತ್ತಿದೆ = difficulty breathing in Kannada
# ಎಚ್ಚರ ತಪ್ಪಿದೆ = lost consciousness in Kannada

fix1_old = "\u0c89\u0c38\u0cbf\u0cb0\u0cbe\u0ca1\u0cb2\u0cc1 \u0c95\u0cb7\u0ccd\u0c9f"
fix2_old = "\u0c8e\u0c9a\u0ccd\u0c9a\u0cb0 \u0ca4\u0caa\u0ccd\u0caa\u0cbf\u0ca6\u0cc6"

# These are the exact strings from triage.py
with open("backend/triage.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check what's in the file
for kw in [fix1_old, fix2_old]:
    if kw in content:
        print(f"Found: {kw}")
    else:
        print(f"NOT found: {kw}")
        print(f"Bytes: {kw.encode('utf-8')}")

# Find all Kannada keywords in file
lines = content.split("\n")
for i, line in enumerate(lines):
    if any(ord(c) > 0x0C80 for c in line):
        print(f"Line {i}: {repr(line)}")
