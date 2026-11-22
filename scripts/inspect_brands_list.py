with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_brand = text.find('function renderBrandsList')
print(text[pos_brand:pos_brand+1800])
