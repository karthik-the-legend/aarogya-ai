import sys
sys.path.insert(0, 'backend')

# The correct Kannada keyword using exact Unicode codepoints
correct_kannada = '\u0c8e\u0ca6\u0cc6 \u0ca8\u0ccb\u0cb5\u0cc1'

print("Correct keyword:", correct_kannada)
print("Correct bytes  :", correct_kannada.encode('utf-8'))

# Read the file
with open('backend/triage.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the problematic line
new_lines = []
for line in lines:
    if '\u0c8e\u0ca6\u0cc6' in line and '\u0ca8\u0ccb\u0cb5' in line:
        new_line = '    "' + correct_kannada + '",\n'
        print("Fixed:", line.strip(), "->", new_line.strip())
        new_lines.append(new_line)
    else:
        new_lines.append(line)

# Write back
with open('backend/triage.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("File saved!")

# Verify
import importlib
import triage
importlib.reload(triage)

test_query = '\u0c8e\u0ca6\u0cc6 \u0ca8\u0ccb\u0cb5\u0cc1'
result = triage.classify(test_query)
print("Test result:", result.level.value)
if result.level.value == 'red':
    print("SUCCESS - Kannada fixed!")
else:
    print("STILL FAILING")