with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="login-modal"')
print(text[pos:pos+3000])
