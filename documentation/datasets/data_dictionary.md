# AutoSense Data Dictionary

This document specifies the unified relational and analytical schema for the AutoSense platform across MySQL, HDFS, Hive, and downstream ML pipelines.

## 1. Table: `reviews` (Core Review Entity)

| Column Name | Data Type | Nullable | Description | Example Value |
|---|---|---|---|---|
| `review_id` | BIGINT (PK) | No | Unique surrogate identifier for the review | `100001` |
| `source_id` | VARCHAR(100) | Yes | Original record ID in source dataset | `REC_001` |
| `source_name` | VARCHAR(100) | No | Identifier of the originating dataset source | `Primary_Auto_1000` |
| `brand` | VARCHAR(100) | Yes | Automobile manufacturer/brand | `Hyundai` |
| `vehicle_model` | VARCHAR(100) | Yes | Vehicle model or variant | `Creta` |
| `review_text_original` | TEXT | No | Exact unaltered raw review text | `"Great mileage and comfortable driving..."` |
| `review_text_processed` | TEXT | Yes | Cleaned, normalized review text | `"great mileage and comfortable driving..."` |
| `language` | VARCHAR(10) | Yes | ISO language code | `en` |
| `review_date` | DATETIME | Yes | Timestamp of review publication | `2026-09-02 12:59:00` |
| `overall_rating` | FLOAT | Yes | User star rating (scale 1.0 - 5.0) | `4.0` |
| `original_sentiment_label` | VARCHAR(20) | Yes | Ground-truth label in source data | `positive` |
| `normalized_sentiment_label` | VARCHAR(20) | No | Standardized ternary label (`positive`, `negative`, `neutral`) | `positive` |
| `created_at` | TIMESTAMP | No | System ingestion timestamp | `CURRENT_TIMESTAMP` |

## 2. Table: `review_aspects` (Normalized Aspect Sentiments)

| Column Name | Data Type | Nullable | Description | Example Value |
|---|---|---|---|---|
| `aspect_id` | BIGINT (PK, Auto) | No | Unique aspect observation identifier | `1` |
| `review_id` | BIGINT (FK) | No | Reference to parent `reviews.review_id` | `100001` |
| `aspect_category` | VARCHAR(50) | No | Normalized AutoSense aspect taxonomy category | `Engine / Performance` |
| `aspect_term` | VARCHAR(100) | Yes | Explicit entity/feature mentioned | `mileage` |
| `opinion_term` | VARCHAR(100) | Yes | Modifier or opinion expression | `great` |
| `aspect_sentiment` | VARCHAR(20) | No | Sentiment polarity for this aspect (`positive`, `negative`, `neutral`) | `positive` |

## 3. Table: `dataset_sources` (Provenance & Governance)

| Column Name | Data Type | Description |
|---|---|---|
| `source_id` | VARCHAR(50) (PK) | Canonical source identifier |
| `source_name` | VARCHAR(150) | Full name of dataset |
| `total_records` | INT | Total records ingested |
| `license_notes` | TEXT | Usage permissions, citation, paper reference |
| `ingestion_status` | VARCHAR(50) | Status: `ACTIVE`, `EVALUATION_ONLY`, `EXCLUDED` |

## 4. AutoSense Aspect Taxonomy Mapping

| Core Aspect Category | Sub-Aspect Keywords & Terms |
|---|---|
| **Performance** | Engine, pickup, acceleration, power, torque, horsepower, top speed, gearbox, transmission |
| **Economy** | Mileage, fuel consumption, kmpl, running cost, EV range, battery efficiency |
| **Comfort** | Suspension, seats, legroom, ride quality, ergonomics, headroom, cabin noise |
| **Safety** | Airbags, braking, ABS, ADAS, crash test, stability, build quality |
| **Design** | Exterior styling, body lines, interior aesthetics, paint, dashboard layout |
| **Technology** | Infotainment, touchscreen, Apple CarPlay, Android Auto, navigation, sensors |
| **Service & Ownership** | Maintenance, dealer service, spare parts availability, warranty, reliability |
| **Value** | Pricing, on-road cost, value for money, resale value |
