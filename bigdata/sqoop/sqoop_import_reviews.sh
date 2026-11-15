#!/usr/bin/env bash
# ==============================================================================
# AutoSense: Big Data Sentiment Analysis Pipeline
# Apache Sqoop 1.4.7 Import Script: MySQL -> Hadoop HDFS
# ==============================================================================
set -euo pipefail

# Configuration parameters
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_DB="${MYSQL_DATABASE:-autosense_db}"
MYSQL_USER="${MYSQL_USER:-autosense_user}"
MYSQL_PASS="${MYSQL_PASSWORD:-autosense_password}"

HDFS_TARGET_DIR="/autosense/raw/reviews"
NUM_MAPPERS=1

echo "======================================================================"
echo "Starting Apache Sqoop 1.4.7 Ingestion: Table 'reviews'"
echo "Source: mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}"
echo "Target HDFS: ${HDFS_TARGET_DIR}"
echo "Start Time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

# Step 1: Ensure target directory is clean
hdfs dfs -rm -r -f "${HDFS_TARGET_DIR}" || true

# Step 2: Execute Sqoop Import
# Using tab-delimiter and escaped newlines to preserve multiline review text
START_TIME=$(date +%s)

sqoop import \
  --connect "jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}?useSSL=false&serverTimezone=UTC&characterEncoding=UTF-8" \
  --username "${MYSQL_USER}" \
  --password "${MYSQL_PASS}" \
  --table reviews \
  --target-dir "${HDFS_TARGET_DIR}" \
  --fields-terminated-by '\t' \
  --lines-terminated-by '\n' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --num-mappers "${NUM_MAPPERS}"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "======================================================================"
echo "Sqoop Ingestion Complete in ${DURATION} seconds"
echo "Verifying HDFS Destination:"
hdfs dfs -ls -h "${HDFS_TARGET_DIR}"
echo "Record Count in HDFS:"
hdfs dfs -cat "${HDFS_TARGET_DIR}/part-*" | wc -l
echo "======================================================================"
