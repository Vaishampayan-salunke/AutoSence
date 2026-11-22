with open('backend/app/routes/api.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('/predict/compare')
print(text[pos+1000:pos+2500])
