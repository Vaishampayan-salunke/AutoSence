with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function runMultiModelComparison')
pos2 = text.find('function renderComparisonResults')
print("Whole function:")
print(text[pos:pos2])
