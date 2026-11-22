with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="model-detail-subview"')
print(text[pos:pos+2000])
