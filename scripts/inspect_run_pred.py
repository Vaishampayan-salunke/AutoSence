content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
idx = content.find('function runSinglePrediction')
print(content[idx:idx+1200])
