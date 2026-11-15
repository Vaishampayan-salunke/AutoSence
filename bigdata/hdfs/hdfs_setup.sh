#!/usr/bin/env bash
# ==============================================================================
# AutoSense HDFS Namespace Setup & Health Verification
# ==============================================================================
set -euo pipefail

echo "Initializing AutoSense HDFS storage hierarchy..."

# Create namespaces
hdfs dfs -mkdir -p /autosense/raw/reviews
hdfs dfs -mkdir -p /autosense/raw/aspects
hdfs dfs -mkdir -p /autosense/warehouse/hive
hdfs dfs -mkdir -p /autosense/logs

# Set permissions
hdfs dfs -chmod -R 755 /autosense

echo "HDFS Directory Structure:"
hdfs dfs -ls -R /autosense
echo "HDFS Health Report:"
hdfs dfsadmin -report
