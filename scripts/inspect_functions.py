with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function renderModelsCatalog', text)]
for m in matches:
    print('Found function renderModelsCatalog at', m)
    print(text[m:m+1200])

matches2 = [m.start() for m in re.finditer(r'function runMultiModelComparison', text)]
for m in matches2:
    print('Found function runMultiModelComparison at', m)
    print(text[m:m+1200])

matches3 = [m.start() for m in re.finditer(r'function runBatchEvaluation', text)]
for m in matches3:
    print('Found function runBatchEvaluation at', m)
    print(text[m:m+1200])
