import re

content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
matches = [m.start() for m in re.finditer(r'view-overview', content)]
print("Occurrences of view-overview:", len(matches))
for idx in matches[:3]:
    start = max(0, idx - 150)
    end = min(len(content), idx + 200)
    print("--- SNIPPET ---")
    print(content[start:end])
