with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="batch-results-box"')
print(text[pos:pos+2000])
