-- ==============================================================================
-- AutoSense Apache Hive Data Warehouse DDL
-- External tables mapped over HDFS Sqoop imports
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS autosense
LOCATION '/autosense/warehouse/hive';

USE autosense;

-- ------------------------------------------------------------------------------
-- External Table: raw_reviews
-- Delimited by Tab to preserve commas inside review text
-- ------------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS raw_reviews (
    review_id BIGINT,
    source_id STRING,
    source_name STRING,
    brand STRING,
    vehicle_model STRING,
    review_text_original STRING,
    review_text_processed STRING,
    language STRING,
    review_date STRING,
    overall_rating FLOAT,
    original_sentiment_label STRING,
    normalized_sentiment_label STRING,
    created_at STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/autosense/raw/reviews';

-- ------------------------------------------------------------------------------
-- External Table: raw_aspects
-- ------------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS raw_aspects (
    aspect_id BIGINT,
    review_id BIGINT,
    aspect_category STRING,
    aspect_term STRING,
    opinion_term STRING,
    aspect_sentiment STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/autosense/raw/aspects';

-- ------------------------------------------------------------------------------
-- Managed Analytics Table: brand_sentiment_summary (ORC Format)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brand_sentiment_summary
STORED AS ORC AS
SELECT 
    brand,
    COUNT(*) as total_reviews,
    SUM(CASE WHEN normalized_sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN normalized_sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN normalized_sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
    ROUND(AVG(overall_rating), 2) as avg_rating
FROM raw_reviews
GROUP BY brand;
