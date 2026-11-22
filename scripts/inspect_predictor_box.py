with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(835, 875):
    print(f"{i+1}: {lines[i]}", end="")
