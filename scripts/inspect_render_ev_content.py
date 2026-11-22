with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function renderEvidenceContent')
print(text[pos:pos+1500])
