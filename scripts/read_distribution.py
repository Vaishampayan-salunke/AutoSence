import csv
from collections import Counter

with open('Datasets/normalized/automobile_reviews_unified_12000.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

total = len(rows)
dist = Counter(r['sentiment'].strip().lower() for r in rows)
print(f"Total: {total}")
for label, count in sorted(dist.items()):
    print(f"  {label}: {count} ({count/total*100:.2f}%)")
