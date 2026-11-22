with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function openModelDetailView')
if pos != -1:
    print(text[pos:pos+2500])
else:
    print('openModelDetailView not found')
