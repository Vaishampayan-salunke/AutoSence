#!/usr/bin/env bash
# ==============================================================================
# AutoSense: Big Data Sentiment Analysis Pipeline
# Apache Sqoop 1.4.7 Import Script: MySQL -> Hadoop HDFS ('review_aspects')
# ==============================================================================
set -euo pipefail

MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_DB="${MYSQL_DATABASE:-autosense_db}"
MYSQL_USER="${MYSQL_USER:-autosense_user}"
MYSQL_PASS="${MYSQL_PASSWORD:-autosense_password}"

HDFS_TARGET_DIR="/autosense/raw/aspects"
NUM_MAPPERS=1

echo "Starting Sqoop Import for 'review_aspects' to ${HDFS_TARGET_DIR}..."
hdfs dfs -rm -r -f "${HDFS_TARGET_DIR}" || true

sqoop import \
  --connect "jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}?useSSL=false&serverTimezone=UTC&characterEncoding=UTF-8" \
  --username "${MYSQL_USER}" \
  --password "${MYSQL_PASS}" \
  --table review_aspects \
  --target-dir "${HDFS_TARGET_DIR}" \
  --fields-terminated-by '\t' \
  --lines-terminated-by '\n' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --num-mappers "${NUM_MAPPERS}"

echo "Review aspects successfully ingested into HDFS."
