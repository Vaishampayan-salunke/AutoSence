import re

content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()

# Print switchView function
match = re.search(r'function\s+switchView\s*\(.*?\)\s*\{.*?\}', content, re.DOTALL)
if match:
    print("switchView function:\n", match.group(0))

# Print all elements calling switchView
calls = re.findall(r'<[^>]*switchView\([^>]*>[^<]*<', content)
print(f"\nElements calling switchView ({len(calls)}):")
for c in calls:
    print(" ", c.strip())
