with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function runMultiModelComparison')
print("--- runMultiModelComparison and renderComparisonResults ---")
print(text[pos:pos+2500])
