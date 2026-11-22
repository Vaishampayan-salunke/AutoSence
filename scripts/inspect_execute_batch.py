with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function executeBatchTest')
if pos != -1:
    print(text[pos:pos+2000])
else:
    print('executeBatchTest not found')
