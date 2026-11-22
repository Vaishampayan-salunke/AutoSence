with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('Big Data Ingestion & Storage Architecture')
if pos == -1:
    pos = text.find('Big Data Ingestion')
print(text[pos:pos+2500])
