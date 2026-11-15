-- ==============================================================================
-- AutoSense Hive Analytical Query Suite
-- Used for big-data aggregation feeding backend caches and research metrics
-- ==============================================================================

USE autosense;

-- Query 1: Vehicle Model Negative Sentiment Hotspots (Complaint Rate Calculation)
-- Complaint Rate = (Negative Aspect Mentions / Total Aspect Mentions) * 100
SELECT 
    r.brand,
    r.vehicle_model,
    a.aspect_category,
    COUNT(*) as total_mentions,
    SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) as negative_mentions,
    ROUND((SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as complaint_percentage
FROM raw_reviews r
JOIN raw_aspects a ON r.review_id = a.review_id
GROUP BY r.brand, r.vehicle_model, a.aspect_category
HAVING COUNT(*) >= 10
ORDER BY complaint_percentage DESC
LIMIT 25;

-- Query 2: Brand-Level Aspect Sentiment Distribution
SELECT 
    r.brand,
    a.aspect_category,
    SUM(CASE WHEN a.aspect_sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN a.aspect_sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
    ROUND(SUM(CASE WHEN a.aspect_sentiment = 'positive' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as positive_ratio
FROM raw_reviews r
JOIN raw_aspects a ON r.review_id = a.review_id
GROUP BY r.brand, a.aspect_category
ORDER BY r.brand, a.aspect_category;

-- Query 3: Monthly Sentiment Trend Analysis
SELECT 
    SUBSTR(review_date, 1, 7) as year_month,
    r.brand,
    COUNT(*) as review_count,
    ROUND(SUM(CASE WHEN normalized_sentiment_label = 'positive' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as positive_pct,
    ROUND(SUM(CASE WHEN normalized_sentiment_label = 'negative' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as negative_pct
FROM raw_reviews r
WHERE review_date IS NOT NULL AND review_date != ''
GROUP BY SUBSTR(review_date, 1, 7), r.brand
ORDER BY year_month, r.brand;
