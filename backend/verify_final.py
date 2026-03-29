import sys
import ast
import os
sys.path.insert(0, 'backend')

files = [
    'backend/config.py',
    'backend/rag_pipeline.py',
    'backend/triage.py',
    'backend/models.py',
    'backend/translate.py',
    'backend/voice_handler.py',
    'backend/main.py',
]

print("=" * 55)
print("  Final Code Review Checklist")
print("=" * 55)

all_passed = True

for filepath in files:
    if not os.path.exists(filepath):
        print(f"  ✗ MISSING: {filepath}")
        all_passed = False
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check syntax
    try:
        ast.parse(content)
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False
        print(f"  ✗ SYNTAX ERROR in {filepath}: {e}")
        all_passed = False

    # Check for debug prints
    debug_found = any(x in content for x in ['print("debug', 'print("test', 'TODO', 'FIXME'])

    # Check for docstrings in functions
    tree        = ast.parse(content)
    functions   = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    no_docstring = [f.name for f in functions if not ast.get_docstring(f)]

    name = filepath.split('/')[-1]
    print(f"\n  {name}:")
    print(f"    Syntax    : {'✓ OK' if syntax_ok else '✗ ERROR'}")
    print(f"    Debug txt : {'✗ Found — remove them' if debug_found else '✓ Clean'}")
    print(f"    Functions : {len(functions)} total")
    if no_docstring:
        print(f"    No docs   : {no_docstring[:3]}")

# Check config.py specifics
print("\n  config.py specifics:")
with open('backend/config.py', 'r', encoding='utf-8') as f:
    cfg = f.read()
print(f"    GEMINI_API_KEY check : {'✓' if 'raise ValueError' in cfg else '✗ Missing'}")
print(f"    CHUNK_SIZE defined   : {'✓' if 'CHUNK_SIZE' in cfg else '✗ Missing'}")
print(f"    SUPPORTED_LANGUAGES  : {'✓' if 'SUPPORTED_LANGUAGES' in cfg else '✗ Missing'}")

# Check triage.py
print("\n  triage.py specifics:")
with open('backend/triage.py', 'r', encoding='utf-8') as f:
    triage = f.read()
kw_count = triage.count('"')  // 2
print(f"    Keywords approx : {kw_count}")
print(f"    Hindi keywords  : {'✓' if 'सीने में दर्द' in triage else '✗ Missing'}")
print(f"    Tamil keywords  : {'✓' if 'மார்பு வலி' in triage else '✗ Missing'}")
print(f"    Telugu keywords : {'✓' if 'ఛాతీ నొప్పి' in triage else '✗ Missing'}")
print(f"    Kannada keywords: {'✓' if 'ಎದೆ ನೋವು' in triage else '✗ Missing'}")

print("\n" + "=" * 55)
print(f"  {'✅ All checks passed!' if all_passed else '⚠️ Fix issues above'}")
print("=" * 55)