with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Check sidebar nav
pos_side = text.find('id="nav-brands"')
print("Sidebar area:")
print(text[pos_side:pos_side+400])

# 2. Check renderBrandsList
pos_brand = text.find('function renderBrandsList')
print("\nrenderBrandsList area:")
print(text[pos_brand:pos_brand+500])

# 3. Check renderModelsCatalog
pos_mod = text.find('function renderModelsCatalog')
print("\nrenderModelsCatalog area:")
print(text[pos_mod:pos_mod+700])

# 4. Check openModelDetailView
pos_det = text.find('function openModelDetailView')
print("\nopenModelDetailView area:")
print(text[pos_det:pos_det+700])
