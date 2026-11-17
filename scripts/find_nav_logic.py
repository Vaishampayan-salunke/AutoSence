import re

content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
# Search for functions that toggle view-
js_matches = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(.*?\)\s*\{', content)
print("JavaScript functions:", js_matches[:25])

# Search for click handlers or data-view attributes
data_views = re.findall(r'data-view=["\'](.*?)["\']', content)
print("Data-views found:", set(data_views))

# Search for onclick
onclicks = re.findall(r'onclick=["\'](.*?)["\']', content)
print("Sample onclicks:", onclicks[:15])
