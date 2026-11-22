with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'id="view-predictor"' in line or 'runBatch' in line or 'Batch Testing' in line or '25 review' in line.lower():
            print(f'{i+1}: {line.strip()[:100]}')
