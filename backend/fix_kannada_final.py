# Fix failing Kannada triage keywords

with open('backend/triage.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The two failing test queries as exact Unicode
kw1 = '\u0c89\u0c38\u0cbf\u0cb0\u0cbe\u0ca1\u0cb2\u0cc1 \u0c95\u0cb7\u0ccd\u0c9f \u0c86\u0c97\u0cc1\u0ca4\u0ccd\u0ca4\u0cbf\u0ca6\u0cc6'
kw2 = '\u0c8e\u0c9a\u0ccd\u0c9a\u0cb0 \u0ca4\u0caa\u0ccd\u0caa\u0cbf\u0ca6'

# Target line to insert before
target = '    "\u0ca4\u0cc0\u0cb5\u0ccd\u0cb0 \u0c9c\u0ccd\u0cb5\u0cb0",'

for kw in [kw1, kw2]:
    if kw not in content:
        content = content.replace(
            target,
            f'    "{kw}",\n{target}'
        )
        print(f'Added: {kw}')
    else:
        print(f'Already exists: {kw}')

with open('backend/triage.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! Testing now...')

# Test immediately
import sys
sys.path.insert(0, 'backend')
import importlib
import triage
importlib.reload(triage)

test1 = '\u0c89\u0c38\u0cbf\u0cb0\u0cbe\u0ca1\u0cb2\u0cc1 \u0c95\u0cb7\u0ccd\u0c9f \u0c86\u0c97\u0cc1\u0ca4\u0ccd\u0ca4\u0cbf\u0ca6\u0cc6'
test2 = '\u0c8e\u0c9a\u0ccd\u0c9a\u0cb0 \u0ca4\u0caa\u0ccd\u0caa\u0cbf\u0ca6\u0cc6'

r1 = triage.classify(test1)
r2 = triage.classify(test2)

print(f'Test 1: {r1.level.value} (expected red) - {"PASS" if r1.level.value == "red" else "FAIL"}')
print(f'Test 2: {r2.level.value} (expected red) - {"PASS" if r2.level.value == "red" else "FAIL"}')