import re

content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
view_ids = re.findall(r'id=["\'](view-[a-zA-Z0-9_-]+)["\']', content)
print("View IDs found:", view_ids)

# Find sidebar buttons/nav items
nav_matches = re.findall(r'(<button[^>]+nav-item[^>]*>.*?<\/button>)', content, re.DOTALL)
print(f"Nav items found ({len(nav_matches)}):")
for n in nav_matches[:10]:
    clean_n = re.sub(r'\s+', ' ', n)
    print(" ", clean_n[:120])
