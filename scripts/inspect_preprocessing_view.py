with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="view-preprocessing"')
print(text[pos:pos+3500])
