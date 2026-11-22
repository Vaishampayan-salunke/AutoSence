with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function renderBatchResult')
pos2 = text.find('function', pos+20)
print(text[pos:pos+2000])
