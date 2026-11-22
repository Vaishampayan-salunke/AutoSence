with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function runMultiModelComparison')
print(text[pos+1200:pos+2500])
