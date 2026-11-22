with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_mod = text.find('function renderModelsCatalog')
print("renderModelsCatalog:")
print(text[pos_mod:pos_mod+1800])

pos_det = text.find('function openModelDetailView')
print("\nopenModelDetailView:")
print(text[pos_det:pos_det+2000])
