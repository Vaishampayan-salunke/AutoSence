import re

content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
matches = [m.start() for m in re.finditer(r'view-brands', content)]
print("Occurrences of view-brands:", len(matches))
for idx in matches:
    start = max(0, idx - 150)
    end = min(len(content), idx + 200)
    print("--- SNIPPET ---")
    print(content[start:end])
