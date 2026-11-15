# AutoSense Production Operations Runbook

## 1. Routine Maintenance & Operations

### A. Refreshing Analytics Caches
When new reviews are ingested into MySQL or SQLite, refresh the analytical cache:
```bash
python -m src.analytics.analytics_engine
```
This updates `reports/analytics_cache.json` which instantly updates all dashboard metrics across brands, models, and aspects without requiring a service restart.

### B. Registering New Trained Models
To train and register new sentiment models:
```bash
# Traditional ML Baselines (TF-IDF + Logistic Regression / SVM / Naive Bayes)
python -m src.models.train_traditional_ml

# Transformer (DistilBERT)
python -m src.models.distilbert_trainer
```
New models are automatically registered in `models/model_registry/model_registry.json` and immediately available in the live predictor dropdown and `/api/predict`.

---

## 2. Big Data Pipeline Telemetry Export

To run the Sqoop/HDFS benchmark simulation and record throughput telemetry:
```bash
python -m src.data.pipeline_benchmark
```
- Telemetry Output: `bigdata/logs/pipeline_execution_log.json`
- Experiment Output: `experiments/experiment_03_pipeline_benchmark/pipeline_benchmark_results.json`

---

## 3. Database Backup & Disaster Recovery

### MySQL Backup:
```bash
mysqldump -u autosense_user -p autosense_db > backup_autosense_$(date +%Y%m%d).sql
```

### Restore:
```bash
mysql -u autosense_user -p autosense_db < backup_autosense_20261115.sql
```

### Local SQLite Database:
The local fallback database is stored at `bigdata/mysql/autosense_local.db`. Back up by simply copying the file while the application is quiescent.

---

## 4. Troubleshooting & Diagnostic Commands

| Issue | Diagnostic Step | Resolution |
|---|---|---|
| Server fails to start | Check port 8000 occupancy: `netstat -ano \| findstr 8000` | Terminate conflicting process or change port via `PORT=8080` |
| Database connection refused | Verify MySQL service or check `DATABASE_URL` in `.env` | Fallback automatically engages SQLite if MySQL is unavailable |
| Model not found error | Inspect `models/model_registry/model_registry.json` | Run `python -m src.models.train_traditional_ml` to recreate artifacts |
| Out of memory during transformer training | Check available system RAM | Adjust `batch_size=8` or `n=150` in `src/models/distilbert_trainer.py` |
