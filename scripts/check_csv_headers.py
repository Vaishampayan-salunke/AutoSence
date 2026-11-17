import csv

with open('Datasets/normalized/automobile_reviews_unified_12000.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    print("Headers:", headers)
    # read a few rows
    for i, row in enumerate(reader):
        if i < 3:
            print(row)
        else:
            break
