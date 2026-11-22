import sqlite3
import json

conn = sqlite3.connect('V:/BDT/bigdata/mysql/autosense_local.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM reviews')
total_reviews = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM review_aspects')
total_aspects = c.fetchone()[0]

c.execute('SELECT COUNT(DISTINCT review_id) FROM review_aspects')
reviews_with_aspects = c.fetchone()[0]

c.execute('''
    SELECT aspect_category, 
           COUNT(*) as total,
           SUM(CASE WHEN aspect_sentiment = 'positive' THEN 1 ELSE 0 END) as pos,
           SUM(CASE WHEN aspect_sentiment = 'neutral' THEN 1 ELSE 0 END) as neu,
           SUM(CASE WHEN aspect_sentiment = 'negative' THEN 1 ELSE 0 END) as neg
    FROM review_aspects
    GROUP BY aspect_category
    ORDER BY total DESC
''')
aspect_rows = c.fetchall()

c.execute('''
    SELECT aspect_category, aspect_term, opinion_term, aspect_sentiment, r.review_text_original, r.brand, r.vehicle_model
    FROM review_aspects ra
    JOIN reviews r ON ra.review_id = r.review_id
    WHERE ra.opinion_term IS NOT NULL AND ra.opinion_term != ''
    LIMIT 10
''')
triplet_samples = c.fetchall()

c.execute('''
    SELECT brand, COUNT(*) as cnt, AVG(overall_rating) as avg_r,
           SUM(CASE WHEN normalized_sentiment_label = 'positive' THEN 1 ELSE 0 END) as pos,
           SUM(CASE WHEN normalized_sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neu,
           SUM(CASE WHEN normalized_sentiment_label = 'negative' THEN 1 ELSE 0 END) as neg
    FROM reviews
    GROUP BY brand
    ORDER BY cnt DESC
''')
brand_rows = c.fetchall()

conn.close()

result = {
    "total_reviews": total_reviews,
    "total_aspect_triplets": total_aspects,
    "distinct_reviews_with_aspects": reviews_with_aspects,
    "aspect_breakdown": [
        {"category": r[0], "total": r[1], "positive": r[2], "neutral": r[3], "negative": r[4]}
        for r in aspect_rows
    ],
    "sample_triplets": [
        {
            "category": r[0],
            "aspect_term": r[1],
            "opinion_term": r[2],
            "sentiment": r[3],
            "brand": r[5],
            "model": r[6],
            "text": r[4][:120] + "..." if len(r[4]) > 120 else r[4]
        }
        for r in triplet_samples
    ],
    "brand_breakdown": [
        {"brand": r[0], "review_count": r[1], "avg_rating": round(r[2], 2), "positive": r[3], "neutral": r[4], "negative": r[5]}
        for r in brand_rows
    ]
}

print(json.dumps(result, indent=2))
with open('V:/BDT/reports/database_counts_reconciled.json', 'w') as f:
    json.dump(result, f, indent=2)
