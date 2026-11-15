"""
AutoSense Research Experiments Runner
Aggregates and executes the 5 core research experiments:
E1: Multi-Model Sentiment Comparison
E2: Aspect-Level Evaluation
E3: Cross-Dataset Generalization
E4: Sqoop/HDFS Big Data Pipeline Performance
E5: Automobile Complaint Hotspot Analysis
"""
import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from src.preprocessing.text_cleaner import clean_automobile_text
from src.models.vader_model import VaderBaseline

def run_all_experiments():
    print("=" * 80)
    print("AutoSense: Executing Complete Research Experiment Suite (Phase 10)")
    print("=" * 80)
    
    # --- Experiment E1: Multi-Model Comparison ---
    print("\n[E1] Consolidating Model Comparison...")
    comp_file = r"V:\BDT\experiments\experiment_01_baseline_comparison\model_comparison.json"
    distilbert_file = r"V:\BDT\experiments\experiment_01_baseline_comparison\distilbert_metrics.json"
    
    e1_data = {}
    if os.path.exists(comp_file):
        with open(comp_file, 'r', encoding='utf-8') as f:
            e1_data = json.load(f)
    if os.path.exists(distilbert_file):
        with open(distilbert_file, 'r', encoding='utf-8') as f:
            d_data = json.load(f)
            e1_data["autosense-distilbert-v1"] = d_data
            
    # --- Experiment E2: Aspect Evaluation ---
    print("\n[E2] Consolidating Aspect-Level Evaluation...")
    absa_file = r"V:\BDT\experiments\experiment_02_aspect_evaluation\aspect_evaluation_results.json"
    e2_data = {}
    if os.path.exists(absa_file):
        with open(absa_file, 'r', encoding='utf-8') as f:
            e2_data = json.load(f)
            
    # --- Experiment E3: Cross-Dataset Generalization ---
    print("\n[E3] Executing Cross-Dataset Generalization Benchmark...")
    # Load primary model (Logistic Regression)
    lr_model_path = r"V:\BDT\models\traditional_ml\autosense-tfidf-lr-v1.joblib"
    e3_results = {}
    if os.path.exists(lr_model_path):
        pipe = joblib.load(lr_model_path)
        
        # Test on Hybrid Car Dataset
        hybrid_fp = r"V:\BDT\Datasets\1000 reviews RS_P-7.xlsx"
        if os.path.exists(hybrid_fp):
            df_h = pd.read_excel(hybrid_fp)
            rows_h = df_h.iloc[1:].copy()
            # Positive=col 18, Neutral=col 19, Negative=col 20
            y_true_h = []
            y_pred_h = []
            for _, r in rows_h.iterrows():
                if r.iloc[18] == 1:
                    gt = 'positive'
                elif r.iloc[20] == 1:
                    gt = 'negative'
                elif r.iloc[19] == 1:
                    gt = 'neutral'
                else:
                    continue
                raw_t = str(r.iloc[1])
                pred = pipe.predict([clean_automobile_text(raw_t)])[0]
                y_true_h.append(gt)
                y_pred_h.append(pred)
                
            acc_h = accuracy_score(y_true_h, y_pred_h)
            p_h, rec_h, f1_h, _ = precision_recall_fscore_support(y_true_h, y_pred_h, average='macro', zero_division=0)
            e3_results["hybrid_car_cross_eval"] = {
                "dataset_name": "Hybrid Car Online Reviews (Manzoor et al., 2022)",
                "sample_size": len(y_true_h),
                "accuracy": round(float(acc_h), 4),
                "macro_f1": round(float(f1_h), 4),
                "macro_precision": round(float(p_h), 4),
                "macro_recall": round(float(rec_h), 4)
            }
            print(f"  Hybrid Car Cross-Dataset Accuracy: {acc_h:.4f}, Macro F1: {f1_h:.4f} (N={len(y_true_h)})")
            
        # Test on Edmunds Dataset (Using star rating as sentiment proxy: 4-5=pos, 3=neu, 1-2=neg)
        edmunds_fp = r"V:\BDT\Datasets\Additional automotive reviews\edmunds_car_reviews.csv"
        if os.path.exists(edmunds_fp):
            df_edm = pd.read_csv(edmunds_fp, engine='python', on_bad_lines='skip')
            df_edm_clean = df_edm[df_edm['Review'].notna() & df_edm['Rating'].notna()].head(1000)
            y_true_e = []
            y_pred_e = []
            for _, r in df_edm_clean.iterrows():
                rating = float(r['Rating'])
                if rating >= 4.0:
                    gt = 'positive'
                elif rating <= 2.5:
                    gt = 'negative'
                else:
                    gt = 'neutral'
                pred = pipe.predict([clean_automobile_text(str(r['Review']))])[0]
                y_true_e.append(gt)
                y_pred_e.append(pred)
                
            acc_e = accuracy_score(y_true_e, y_pred_e)
            p_e, rec_e, f1_e, _ = precision_recall_fscore_support(y_true_e, y_pred_e, average='macro', zero_division=0)
            e3_results["edmunds_cross_eval"] = {
                "dataset_name": "Edmunds Consumer Car Reviews",
                "sample_size": len(y_true_e),
                "accuracy": round(float(acc_e), 4),
                "macro_f1": round(float(f1_e), 4),
                "macro_precision": round(float(p_e), 4),
                "macro_recall": round(float(rec_e), 4)
            }
            print(f"  Edmunds Cross-Dataset Accuracy:    {acc_e:.4f}, Macro F1: {f1_e:.4f} (N={len(y_true_e)})")

    # --- Experiment E4: Big Data Pipeline Performance ---
    print("\n[E4] Loading Pipeline Benchmark Telemetry...")
    pipe_file = r"V:\BDT\experiments\experiment_03_pipeline_benchmark\pipeline_benchmark_results.json"
    e4_data = {}
    if os.path.exists(pipe_file):
        with open(pipe_file, 'r', encoding='utf-8') as f:
            e4_data = json.load(f)

    # --- Experiment E5: Complaint Hotspots ---
    print("\n[E5] Calculating Complaint Hotspots...")
    from src.data.database import get_session, Review, ReviewAspect
    session = get_session()
    
    aspects = session.query(ReviewAspect, Review).join(Review, ReviewAspect.review_id == Review.review_id).all()
    
    # Group by (brand, aspect_category)
    complaint_stats = {}
    for asp, rev in aspects:
        key = (rev.brand or 'General', asp.aspect_category)
        if key not in complaint_stats:
            complaint_stats[key] = {'total': 0, 'negative': 0, 'samples': []}
        complaint_stats[key]['total'] += 1
        if asp.aspect_sentiment == 'negative':
            complaint_stats[key]['negative'] += 1
            if len(complaint_stats[key]['samples']) < 2:
                complaint_stats[key]['samples'].append(rev.review_text_original)
                
    e5_hotspots = []
    for (brand, cat), stat in complaint_stats.items():
        if stat['total'] >= 15: # Support count threshold
            neg_rate = round((stat['negative'] / stat['total']) * 100, 2)
            e5_hotspots.append({
                "brand": brand,
                "aspect_category": cat,
                "total_mentions": stat['total'],
                "negative_mentions": stat['negative'],
                "complaint_rate_pct": neg_rate,
                "supporting_sample": stat['samples'][0] if stat['samples'] else None
            })
    e5_hotspots.sort(key=lambda x: x['complaint_rate_pct'], reverse=True)
    session.close()
    print(f"  Identified {len(e5_hotspots)} robust complaint hotspots across brands.")

    # --- Master Consolidation ---
    master_report = {
        "title": "AutoSense Comprehensive Research Experiments & Evaluation",
        "E1_model_comparison": e1_data,
        "E2_aspect_evaluation": e2_data,
        "E3_cross_dataset_generalization": e3_results,
        "E4_big_data_pipeline_telemetry": e4_data,
        "E5_top_complaint_hotspots": e5_hotspots[:10]
    }
    
    summary_path = r"V:\BDT\reports\research_evaluation_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(master_report, f, indent=2)
        
    md_path = r"V:\BDT\documentation\experiments\research_findings.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# AutoSense Research Experiments & Empirical Evaluation\n\n")
        f.write("## Experiment E1: Sentiment Model Comparison (Held-Out Test Set)\n\n")
        f.write("| Model Version | Architecture | Accuracy | Macro F1 | Weighted F1 |\n")
        f.write("|---|---|---|---|---|\n")
        for mid, m in e1_data.items():
            f.write(f"| `{mid}` | {m.get('name', mid)} | {m.get('test_accuracy', 0):.4f} | {m.get('test_macro_f1', 0):.4f} | {m.get('test_weighted_f1', 0):.4f} |\n")
            
        f.write("\n## Experiment E3: Cross-Dataset Generalization\n\n")
        f.write("| Benchmark Dataset | Sample Size | Accuracy | Macro F1 |\n")
        f.write("|---|---|---|---|\n")
        for k, v in e3_results.items():
            f.write(f"| {v['dataset_name']} | {v['sample_size']} | {v['accuracy']:.4f} | {v['macro_f1']:.4f} |\n")
            
        f.write("\n## Experiment E4: Apache Sqoop & Big Data Pipeline Performance\n\n")
        if e4_data:
            f.write(f"- **Total Records Ingested:** {e4_data.get('total_records')}\n")
            f.write(f"- **Overall Pipeline Throughput:** {e4_data.get('stages', [{}])[0].get('throughput_records_per_sec')} records/sec\n")
            f.write(f"- **Payload Transferred:** {e4_data.get('total_payload_kb')} KB\n")
            
        f.write("\n## Experiment E5: Automobile Complaint Hotspots (Top 5)\n\n")
        f.write("| Brand | Aspect Category | Complaint Rate (%) | Negative Mentions | Total Mentions |\n")
        f.write("|---|---|---|---|---|\n")
        for h in e5_hotspots[:5]:
            f.write(f"| {h['brand']} | {h['aspect_category']} | **{h['complaint_rate_pct']}%** | {h['negative_mentions']} | {h['total_mentions']} |\n")
            
    print(f"\nMaster Research Summary saved to {summary_path} and {md_path}")
    print("=" * 80)

if __name__ == '__main__':
    run_all_experiments()
