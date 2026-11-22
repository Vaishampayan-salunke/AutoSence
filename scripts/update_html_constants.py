with open('V:/BDT/frontend/dist/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacements = [
    # 1. Update hardcoded top context bar
    ('12,000 Reviews <span class="badge-verified" title="Datasets/normalized/automobile_reviews_unified_12000.csv">VERIFIED</span>',
     '15,000 DB Reviews (12,000 Curated) <span class="badge-verified" title="Reconciled: 15,000 SQLite DB, 12,000 unified CSV">VERIFIED</span>'),
    
    # 2. Update split description in context bar
    ('70/15/15 (Leak-Free) <span class="badge-verified" title="Stratified, seed=42">VERIFIED</span>',
     '70/15/15: 10,500 / 2,250 / 2,250 (Seed 42) <span class="badge-verified" title="0 train/test review_id overlap">VERIFIED</span>'),

    # 3. Update ABSA count in context bar
    ('27,778 Aspects <span class="badge-verified" title="8 Locked Categories">VERIFIED</span>',
     '27,778 Aspect Triplets (13,170 Reviews) <span class="badge-verified" title="27,778 aspect-opinion-sentiment triplets in SQLite">VERIFIED</span>'),

    # 4. Old accuracy fallback
    ('confidence_percentage: 90.56,', 'confidence_percentage: 93.00,'),
    ('Linear SVM (90.6%)', 'Linear SVM (93.00%)'),
    ('EXP-002 — 90.56% test accuracy', 'EXP-002 — 93.00% test accuracy'),
    ('90.56% <span class="badge-verified"', '93.00% <span class="badge-verified"'),
]

for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        print(f"Replaced: {old[:40]}... -> {new[:40]}...")

with open('V:/BDT/frontend/dist/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html text occurrences.")
