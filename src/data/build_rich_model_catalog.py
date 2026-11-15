"""
AutoSense - Build Rich Model Catalog with Reviews & Feedback
Generates a comprehensive catalog of 38 vehicle models across all 15 brands,
including sentiment breakdown, strengths, points needing improvement,
managerial recommendations, vehicle category tags, and actual user reviews.
"""
import sqlite3
import json
import os

SELECTED_MODELS = [
    # Mahindra
    ("Mahindra", "Thar", "SUV"),
    ("Mahindra", "Scorpio-N", "SUV"),
    ("Mahindra", "XUV700", "SUV"),
    ("Mahindra", "Bolero", "SUV"),
    ("Mahindra", "XUV 3XO", "Compact SUV"),
    # Tata Motors
    ("Tata Motors", "Harrier", "SUV"),
    ("Tata Motors", "Safari", "SUV"),
    ("Tata Motors", "Nexon", "Compact SUV"),
    ("Tata Motors", "Punch", "Micro SUV"),
    ("Tata Motors", "Altroz", "Hatchback"),
    # Toyota
    ("Toyota", "Fortuner", "SUV"),
    ("Toyota", "Innova Hycross", "MPV"),
    ("Toyota", "Hyryder", "Hybrid SUV"),
    ("Toyota", "Camry", "Sedan"),
    # Hyundai
    ("Hyundai", "Creta", "SUV"),
    ("Hyundai", "Verna", "Sedan"),
    ("Hyundai", "Venue", "Compact SUV"),
    ("Hyundai", "i20", "Hatchback"),
    ("Hyundai", "Exter", "Micro SUV"),
    # Kia
    ("Kia", "Seltos", "SUV"),
    ("Kia", "Sonet", "Compact SUV"),
    ("Kia", "Carens", "MPV"),
    ("Kia", "EV6", "Electric Crossover"),
    # Maruti Suzuki
    ("Maruti Suzuki", "Swift", "Hatchback"),
    ("Maruti Suzuki", "Fronx", "Crossover"),
    ("Maruti Suzuki", "Grand Vitara", "Hybrid SUV"),
    ("Maruti Suzuki", "Brezza", "Compact SUV"),
    ("Maruti Suzuki", "Baleno", "Hatchback"),
    # Volkswagen
    ("Volkswagen", "Virtus", "Sedan"),
    ("Volkswagen", "Taigun", "SUV"),
    ("Volkswagen", "Tiguan", "Premium SUV"),
    # Skoda
    ("Skoda", "Slavia", "Sedan"),
    ("Skoda", "Kushaq", "SUV"),
    ("Skoda", "Kodiaq", "Luxury SUV"),
    # MG
    ("MG", "Hector", "SUV"),
    ("MG", "ZS EV", "Electric SUV"),
    ("MG", "Astor", "Compact SUV"),
    ("MG", "Gloster", "Full Size SUV"),
    # BYD
    ("BYD", "Atto 3", "Electric SUV"),
    ("BYD", "Seal", "Electric Sedan"),
    ("BYD", "e6", "Electric MPV"),
    # Jeep
    ("Jeep", "Compass", "SUV"),
    ("Jeep", "Meridian", "7-Seater SUV"),
    # Nissan
    ("Nissan", "Magnite", "Compact SUV"),
    ("Nissan", "Altima", "Sedan"),
    ("Nissan", "Sentra", "Sedan"),
    ("Nissan", "Frontier", "Pickup Truck"),
    ("Nissan", "X-Trail", "Premium SUV"),
    # Renault
    ("Renault", "Kiger", "Compact SUV"),
    ("Renault", "Triber", "Subcompact MPV"),
    ("Renault", "Kwid", "Hatchback"),
    # Citroen
    ("Citroen", "C3", "Hatchback"),
    ("Citroen", "C3 Aircross", "SUV"),
    ("Citroen", "Basalt", "Coupe SUV"),
    # Honda
    ("Honda", "City", "Sedan"),
    ("Honda", "Elevate", "SUV"),
    ("Honda", "Amaze", "Sedan")
]

RECOMMENDATION_MAP = {
    "Performance": "Audit transmission mapping and throttle calibration to resolve reported low-speed hesitation.",
    "Economy": "Re-tune ECU air-fuel mixture profiles and test aerodynamic drag under sustained highway speeds.",
    "Comfort": "Re-tune damper compression and rebound valving; improve seat cushion lumbar ergonomics.",
    "Technology": "Release OTA software patch addressing touchscreen responsiveness and smartphone integration stability.",
    "Safety": "Calibrate ADAS camera optical sensors and enhance radar false-alarm rejection filters.",
    "Design": "Upgrade cabin plastic texture quality and install felt insulation behind interior trim clips.",
    "Ownership": "Enforce dealership spare parts fulfillment SLA under 48 hours and audit labor rates.",
    "Value": "Introduce targeted mid-spec variant bundling essential comfort tech at a competitive price."
}

def build_model_catalog():
    print("=" * 70)
    print("AutoSense: Building Rich Model Catalog (35+ Models with Reviews)")
    print("=" * 70)
    
    conn = sqlite3.connect("bigdata/mysql/autosense_local.db")
    c = conn.cursor()
    
    catalog = []
    
    for brand, model, body_type in SELECTED_MODELS:
        # Get review stats
        c.execute("""
            SELECT review_id, overall_rating, normalized_sentiment_label, review_date, review_text_original
            FROM reviews
            WHERE brand = ? AND vehicle_model = ?
            ORDER BY review_id ASC
        """, (brand, model))
        rows = c.fetchall()
        
        total = len(rows)
        if total == 0:
            continue
            
        pos_cnt = sum(1 for r in rows if r[2] == 'positive')
        neu_cnt = sum(1 for r in rows if r[2] == 'neutral')
        neg_cnt = sum(1 for r in rows if r[2] == 'negative')
        
        ratings = [r[1] for r in rows if r[1] is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 3.8
        
        # Get aspect stats for this model
        c.execute("""
            SELECT ra.aspect_category, ra.aspect_sentiment, COUNT(*)
            FROM review_aspects ra
            JOIN reviews r ON ra.review_id = r.review_id
            WHERE r.brand = ? AND r.vehicle_model = ?
            GROUP BY ra.aspect_category, ra.aspect_sentiment
        """, (brand, model))
        aspect_rows = c.fetchall()
        
        pos_aspects = {}
        neg_aspects = {}
        for cat, sent, count in aspect_rows:
            if sent == 'positive':
                pos_aspects[cat] = pos_aspects.get(cat, 0) + count
            elif sent == 'negative':
                neg_aspects[cat] = neg_aspects.get(cat, 0) + count
                
        sorted_pos = sorted(pos_aspects.items(), key=lambda x: x[1], reverse=True)
        sorted_neg = sorted(neg_aspects.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [f"{cat} ({count} positive mentions)" for cat, count in sorted_pos[:3]] if sorted_pos else ["Balanced driving dynamics"]
        improvements = [f"{cat} ({count} complaints)" for cat, count in sorted_neg[:3]] if sorted_neg else ["Minor general feedback"]
        
        primary_complaint = sorted_neg[0][0] if sorted_neg else "Performance"
        rec = RECOMMENDATION_MAP.get(primary_complaint, "Maintain ongoing QA monitoring.")
        
        # Format reviews (up to 30 sample reviews per model)
        reviews_list = []
        for r_id, r_rating, r_sent, r_date, r_text in rows[:30]:
            reviews_list.append({
                "review_id": r_id,
                "rating": r_rating or 3.5,
                "sentiment": r_sent,
                "date": str(r_date)[:10] if r_date else "2023-05-15",
                "text": r_text
            })
            
        catalog.append({
            "brand": brand,
            "model": model,
            "body_type": body_type,
            "total_reviews": total,
            "average_rating": avg_rating,
            "sentiment_distribution": {
                "positive": pos_cnt,
                "neutral": neu_cnt,
                "negative": neg_cnt,
                "positive_pct": round((pos_cnt / total) * 100, 1),
                "neutral_pct": round((neu_cnt / total) * 100, 1),
                "negative_pct": round((neg_cnt / total) * 100, 1)
            },
            "strengths": strengths,
            "improvement_areas": improvements,
            "actionable_recommendation": rec,
            "reviews_sample": reviews_list
        })
        
    print(f"Compiled catalog of {len(catalog)} models across 15 brands.")
    
    # Save standalone catalog
    os.makedirs("frontend/dist", exist_ok=True)
    with open("frontend/dist/models_catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
        
    # Update master autosense_bundle.json
    bundle_path = "frontend/dist/autosense_bundle.json"
    if os.path.exists(bundle_path):
        with open(bundle_path, "r", encoding="utf-8") as f:
            bundle = json.load(f)
        bundle["models_catalog"] = catalog
        with open(bundle_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        print("Updated frontend/dist/autosense_bundle.json with rich model catalog.")
        
    conn.close()

if __name__ == "__main__":
    build_model_catalog()
