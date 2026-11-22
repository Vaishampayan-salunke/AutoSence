with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 24411
print(text[pos-400:pos+1500])
