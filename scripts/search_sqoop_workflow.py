with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('Apache Sqoop')
while pos != -1:
    print(f"Match at {pos}: {text[pos-40:pos+120]}")
    pos = text.find('Apache Sqoop', pos+1)
