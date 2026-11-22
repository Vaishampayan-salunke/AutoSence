with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('<style>')
print(text[pos:pos+2500])
