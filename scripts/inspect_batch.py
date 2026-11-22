with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('runBatchEvaluation')
while pos != -1:
    print(f"Match at {pos}:")
    print(text[pos:pos+1500])
    pos = text.find('runBatchEvaluation', pos+1)
