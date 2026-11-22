with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function runMultiModelComparison')
print(text[pos+500:pos+2000])
