-- ============================================================================
-- AutoSense: Big Data Sentiment Analysis for the Automobile Industry
-- MySQL Production Schema DDL
-- Database: autosense_db
-- Character Set: utf8mb4 (handles emojis, automotive symbols, special punctuation)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS autosense_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE autosense_db;

-- ----------------------------------------------------------------------------
-- Table 1: dataset_sources (Metadata & Provenance)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dataset_sources (
    source_id VARCHAR(50) PRIMARY KEY,
    source_name VARCHAR(150) NOT NULL,
    total_records INT NOT NULL DEFAULT 0,
    license_notes TEXT,
    ingestion_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 2: reviews (Primary Review Entity)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id BIGINT PRIMARY KEY,
    source_id VARCHAR(50),
    source_name VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    vehicle_model VARCHAR(100),
    review_text_original TEXT NOT NULL,
    review_text_processed TEXT,
    language VARCHAR(10) DEFAULT 'en',
    review_date DATETIME,
    overall_rating FLOAT,
    original_sentiment_label VARCHAR(20),
    normalized_sentiment_label VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_brand (brand),
    INDEX idx_model (vehicle_model),
    INDEX idx_sentiment (normalized_sentiment_label),
    INDEX idx_date (review_date),
    INDEX idx_rating (overall_rating),
    FOREIGN KEY (source_id) REFERENCES dataset_sources(source_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 3: review_aspects (Aspect Observations linked to Reviews)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS review_aspects (
    aspect_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    review_id BIGINT NOT NULL,
    aspect_category VARCHAR(50) NOT NULL,
    aspect_term VARCHAR(100),
    opinion_term VARCHAR(100),
    aspect_sentiment VARCHAR(20) NOT NULL,
    INDEX idx_aspect_category (aspect_category),
    INDEX idx_aspect_sentiment (aspect_sentiment),
    INDEX idx_review_aspect (review_id, aspect_category),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 4: model_versions (Registered Model Artifacts)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_versions (
    model_version_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_family VARCHAR(50) NOT NULL, -- 'VADER', 'TRADITIONAL_ML', 'TRANSFORMER'
    artifact_path VARCHAR(255),
    hyperparameters JSON,
    test_accuracy FLOAT,
    test_macro_f1 FLOAT,
    test_weighted_f1 FLOAT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 5: sqoop_import_logs (Big Data Pipeline Telemetry)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sqoop_import_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_table VARCHAR(100) NOT NULL,
    hdfs_target_dir VARCHAR(255) NOT NULL,
    records_transferred INT NOT NULL,
    duration_seconds FLOAT NOT NULL,
    throughput_records_sec FLOAT NOT NULL,
    num_mappers INT NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL, -- 'SUCCESS', 'FAILED'
    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
