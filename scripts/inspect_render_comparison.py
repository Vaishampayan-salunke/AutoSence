with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function renderComparisonResults')
print("--- renderComparisonResults and batch ---")
print(text[pos:pos+3000])
