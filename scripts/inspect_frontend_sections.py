with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('renderModelsCatalog')
if pos != -1:
    print(text[pos:pos+2000])
else:
    for m in re.finditer(r'renderModels\w*', text):
        print(m.group())

pos2 = text.find('runMultiModelComparison')
if pos2 != -1:
    print("--- MULTI MODEL COMPARISON ---")
    print(text[pos2:pos2+1500])
