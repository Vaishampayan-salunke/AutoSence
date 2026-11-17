content = open('V:/BDT/frontend/dist/index.html', encoding='utf-8').read()
idx = content.find('id="view-predictor"')
print(content[idx:idx+1500])
