with open('V:/BDT/frontend/dist/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('</body>')
print("Snippet before body close:")
print(html[idx-400:idx])
