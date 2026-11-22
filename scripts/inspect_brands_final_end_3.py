with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function renderBrandsList')
print(text[pos+900:pos+1600])
