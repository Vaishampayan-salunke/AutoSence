with open('backend/app/routes/api.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('/predict/compare')
print(text[pos:pos+1500])
