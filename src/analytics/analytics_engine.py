"""
AutoSense Analytics Engine
Calculates business, engineering, and research metrics:
1. Overview KPI metrics (Totals, Sentiment distribution, Ratings, Brands, Models).
2. 15-Brand sentiment comparisons and rankings.
3. 60+ Vehicle model drill-down (What is working well vs. Points needing improvement).
4. Locked 8-Aspect breakdown (Performance, Economy, Comfort, Technology, Safety, Design, Ownership, Value).
5. Evidence-backed complaint hotspots with actionable manager recommendations.
6. Multi-graph temporal and comparative analytics structures.
7. Fast caching into reports/analytics_cache.json.
"""
import os
import json
import pandas as pd
from datetime import datetime
from src.data.database import get_session, Review, ReviewAspect
from src.preprocessing.taxonomy import AUTOMOTIVE_TAXONOMY

RECOMMENDATION_LEXICON = {
    "Performance": "Audit transmission calibration and throttle map; investigate low-end torque lags and gear hunting.",
    "Economy": "Optimize ECU fuel-air curves and test aerodynamic drag coefficient under highway cruising speeds.",
    "Comfort": "Re-tune rear damper rebound damping and improve multi-density foam contouring in driver lumbar zone.",
    "Technology": "Deploy OTA firmware update addressing touchscreen latency, Bluetooth disconnects, and wireless CarPlay stability.",
    "Safety": "Calibrate ADAS camera optical thresholds and emergency braking sensitivity to reduce false alerts.",
    "Design": "Upgrade dashboard and door card plastic texture; insulate clip fasteners to eliminate cabin rattles.",
    "Ownership": "Enforce dealership spare parts SLA under 48 hours and implement standard labor pricing schedules.",
    "Value": "Introduce mid-spec value pack variant bundling alloy wheels and reverse camera at competitive MSRP."
}

class AnalyticsEngine:
    def __init__(self):
        self.cache_path = r"V:\BDT\reports\analytics_cache.json"
        
    def generate_analytics_cache(self) -> dict:
        print("Analytics Engine: Compiling Automobile Insights from Database...")
        session = get_session()
        reviews = session.query(Review).all()
        aspects = session.query(ReviewAspect, Review).join(Review, ReviewAspect.review_id == Review.review_id).all()
        
        total_reviews = len(reviews)
        sent_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        brand_reviews = {}
        model_reviews = {}
        date_records = []
        ratings = []
        
        for r in reviews:
            s = r.normalized_sentiment_label.lower()
            sent_counts[s] = sent_counts.get(s, 0) + 1
            if r.overall_rating is not None:
                ratings.append(r.overall_rating)
                
            b = r.brand or "Unknown"
            if b not in brand_reviews:
                brand_reviews[b] = {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0, 'ratings': [], 'models': set()}
            brand_reviews[b]['total'] += 1
            brand_reviews[b][s] += 1
            if r.vehicle_model:
                brand_reviews[b]['models'].add(r.vehicle_model)
            if r.overall_rating is not None:
                brand_reviews[b]['ratings'].append(r.overall_rating)
                
            m = r.vehicle_model or "Unknown"
            if m not in model_reviews:
                model_reviews[m] = {
                    'brand': b,
                    'total': 0,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'ratings': [],
                    'positive_aspects': {},
                    'negative_aspects': {},
                    'sample_reviews_pos': [],
                    'sample_reviews_neg': []
                }
            model_reviews[m]['total'] += 1
            model_reviews[m][s] += 1
            if r.overall_rating is not None:
                model_reviews[m]['ratings'].append(r.overall_rating)
                
            # Sample quotes
            if s == 'positive' and len(model_reviews[m]['sample_reviews_pos']) < 3:
                model_reviews[m]['sample_reviews_pos'].append({
                    "id": r.review_id,
                    "text": r.review_text_original[:160] + "...",
                    "rating": r.overall_rating
                })
            elif s == 'negative' and len(model_reviews[m]['sample_reviews_neg']) < 3:
                model_reviews[m]['sample_reviews_neg'].append({
                    "id": r.review_id,
                    "text": r.review_text_original[:160] + "...",
                    "rating": r.overall_rating
                })
                
            if r.review_date:
                ym = r.review_date.strftime("%Y-%m")
                date_records.append({'month': ym, 'sentiment': s, 'brand': b})
                
        # 1. Brand Summary Table
        brand_summary = []
        for b, data in brand_reviews.items():
            tot = data['total']
            avg_r = round(sum(data['ratings'])/len(data['ratings']), 2) if data['ratings'] else 0.0
            brand_summary.append({
                "brand": b,
                "total_reviews": tot,
                "positive": data['positive'],
                "negative": data['negative'],
                "neutral": data['neutral'],
                "positive_pct": round((data['positive'] / tot) * 100, 1),
                "negative_pct": round((data['negative'] / tot) * 100, 1),
                "neutral_pct": round((data['neutral'] / tot) * 100, 1),
                "average_rating": avg_r,
                "models_count": len(data['models']),
                "models_list": sorted(list(data['models']))[:8]
            })
        brand_summary.sort(key=lambda x: x['total_reviews'], reverse=True)
        
        # 2. Aspect Breakdown & Model Aspect Attribution
        aspect_breakdown = {}
        complaint_map = {}
        
        for asp, rev in aspects:
            cat = asp.aspect_category
            if cat not in aspect_breakdown:
                aspect_breakdown[cat] = {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
            aspect_breakdown[cat]['total'] += 1
            pol = asp.aspect_sentiment.lower()
            aspect_breakdown[cat][pol] = aspect_breakdown[cat].get(pol, 0) + 1
            
            # Map into model aspect counts
            m = rev.vehicle_model or "Unknown"
            if m in model_reviews:
                if pol == 'positive':
                    model_reviews[m]['positive_aspects'][cat] = model_reviews[m]['positive_aspects'].get(cat, 0) + 1
                elif pol == 'negative':
                    model_reviews[m]['negative_aspects'][cat] = model_reviews[m]['negative_aspects'].get(cat, 0) + 1
                    
            # Complaint map
            key = (rev.brand, rev.vehicle_model, cat)
            if key not in complaint_map:
                complaint_map[key] = {'total': 0, 'negative': 0, 'evidence': []}
            complaint_map[key]['total'] += 1
            if pol == 'negative':
                complaint_map[key]['negative'] += 1
                if len(complaint_map[key]['evidence']) < 2:
                    complaint_map[key]['evidence'].append({
                        "review_id": rev.review_id,
                        "text": rev.review_text_original,
                        "date": str(rev.review_date) if rev.review_date else None,
                        "rating": rev.overall_rating
                    })
                    
        aspect_summary = []
        for cat, data in aspect_breakdown.items():
            tot = data['total']
            aspect_summary.append({
                "aspect_category": cat,
                "total_mentions": tot,
                "positive": data['positive'],
                "negative": data['negative'],
                "neutral": data['neutral'],
                "positive_pct": round((data['positive'] / tot) * 100, 1),
                "negative_pct": round((data['negative'] / tot) * 100, 1),
                "neutral_pct": round((data['neutral'] / tot) * 100, 1)
            })
        aspect_summary.sort(key=lambda x: x['total_mentions'], reverse=True)
        
        # 3. Model Drill-down with Executive Pros / Cons
        model_drilldown = []
        for m, data in model_reviews.items():
            tot = data['total']
            avg_r = round(sum(data['ratings'])/len(data['ratings']), 2) if data['ratings'] else 0.0
            
            top_pros = sorted(data['positive_aspects'].items(), key=lambda x: x[1], reverse=True)
            top_cons = sorted(data['negative_aspects'].items(), key=lambda x: x[1], reverse=True)
            
            pro_str = ", ".join([f"{k} ({v} mentions)" for k, v in top_pros[:3]]) if top_pros else "Balanced overall feedback"
            con_str = ", ".join([f"{k} ({v} complaints)" for k, v in top_cons[:3]]) if top_cons else "Minimal reported complaints"
            
            rec = RECOMMENDATION_LEXICON.get(top_cons[0][0], "Maintain ongoing QA monitoring.") if top_cons else "Model customer satisfaction is strong."
            
            model_drilldown.append({
                "model": m,
                "brand": data['brand'],
                "total_reviews": tot,
                "average_rating": avg_r,
                "positive_pct": round((data['positive'] / tot) * 100, 1),
                "negative_pct": round((data['negative'] / tot) * 100, 1),
                "neutral_pct": round((data['neutral'] / tot) * 100, 1),
                "top_strengths": pro_str,
                "improvement_areas": con_str,
                "actionable_recommendation": rec,
                "positive_quotes": data['sample_reviews_pos'],
                "critical_quotes": data['sample_reviews_neg']
            })
        model_drilldown.sort(key=lambda x: x['total_reviews'], reverse=True)
        
        # 4. Actionable Complaint Hotspots
        hotspots = []
        for (b, m, cat), stat in complaint_map.items():
            if stat['total'] >= 6 and stat['negative'] >= 2:
                neg_rate = round((stat['negative'] / stat['total']) * 100, 1)
                rec = RECOMMENDATION_LEXICON.get(cat, "Perform root cause engineering audit.")
                hotspots.append({
                    "brand": b,
                    "model": m,
                    "aspect_category": cat,
                    "total_mentions": stat['total'],
                    "negative_mentions": stat['negative'],
                    "complaint_rate_pct": neg_rate,
                    "recommended_action": rec,
                    "evidence_reviews": stat['evidence']
                })
        hotspots.sort(key=lambda x: (x['complaint_rate_pct'], x['negative_mentions']), reverse=True)
        
        # 5. Monthly Trends
        df_trends = pd.DataFrame(date_records)
        trend_summary = []
        if not df_trends.empty:
            for ym, grp in df_trends.groupby('month'):
                tot = len(grp)
                pos = (grp['sentiment'] == 'positive').sum()
                neg = (grp['sentiment'] == 'negative').sum()
                neu = (grp['sentiment'] == 'neutral').sum()
                trend_summary.append({
                    "month": ym,
                    "total_reviews": int(tot),
                    "positive_pct": round((pos / tot) * 100, 1),
                    "negative_pct": round((neg / tot) * 100, 1),
                    "neutral_pct": round((neu / tot) * 100, 1)
                })
            trend_summary.sort(key=lambda x: x['month'])
            
        session.close()
        
        analytics_payload = {
            "last_updated": datetime.utcnow().isoformat(),
            "kpi": {
                "total_reviews": total_reviews,
                "positive_reviews": sent_counts['positive'],
                "negative_reviews": sent_counts['negative'],
                "neutral_reviews": sent_counts['neutral'],
                "positive_pct": round((sent_counts['positive'] / max(total_reviews, 1)) * 100, 1),
                "negative_pct": round((sent_counts['negative'] / max(total_reviews, 1)) * 100, 1),
                "neutral_pct": round((sent_counts['neutral'] / max(total_reviews, 1)) * 100, 1),
                "average_rating": round(sum(ratings)/len(ratings), 2) if ratings else 0.0,
                "total_brands": len(brand_reviews),
                "total_models": len(model_reviews)
            },
            "brand_analytics": brand_summary,
            "model_drilldown": model_drilldown,
            "aspect_analytics": aspect_summary,
            "complaint_hotspots": hotspots[:30],
            "monthly_trends": trend_summary
        }
        
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(analytics_payload, f, indent=2)
            
        print(f"Analytics cache saved to {self.cache_path}")
        return analytics_payload

    def get_cached_analytics(self) -> dict:
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.generate_analytics_cache()

if __name__ == '__main__':
    engine = AnalyticsEngine()
    data = engine.generate_analytics_cache()
    print("KPIs:", data['kpi'])
    print(f"Computed {len(data['brand_analytics'])} brands, {len(data['model_drilldown'])} models, {len(data['complaint_hotspots'])} complaint hotspots.")
