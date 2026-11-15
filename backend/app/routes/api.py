"""
AutoSense Unified FastAPI API Router
Exposes endpoints for dashboard analytics, explainable sentiment prediction,
batch processing, domain chatbot ("AutoSense AI Copilot"), and big data telemetry.
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Query
import os
import json
import pandas as pd
from typing import Optional, List
from backend.app.schemas.schemas import (
    Token, UserLogin, UserRegister, UserProfile,
    PredictRequest, PredictResponse, BatchPredictRequest,
    ChatRequest, ChatResponse, ReviewSearchResponse, ReviewItem
)
from backend.app.services.auth_service import (
    USERS_DB, verify_password, hash_password, create_access_token, decode_token
)
from src.analytics.analytics_engine import AnalyticsEngine
from src.analytics.chatbot import AutoSenseChatbot
from src.prediction.predict import AutoSensePredictor
from src.preprocessing.taxonomy import get_taxonomy_summary, AUTOMOTIVE_TAXONOMY
from src.data.database import get_session, Review

router = APIRouter(prefix="/api")
analytics_engine = AnalyticsEngine()
chatbot = AutoSenseChatbot()
predictor_cache = {}

def get_predictor(version: str = "autosense-tfidf-lr-v1") -> AutoSensePredictor:
    if version not in predictor_cache:
        predictor_cache[version] = AutoSensePredictor(version)
    return predictor_cache[version]

def get_current_user(authorization: Optional[str] = Header(None)) -> UserProfile:
    if not authorization:
        return UserProfile(username="guest", role="analyst", is_active=True)
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        username = payload["sub"]
        user = USERS_DB.get(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return UserProfile(username=user["username"], role=user["role"], is_active=user["is_active"])
    except Exception:
        return UserProfile(username="guest", role="analyst", is_active=True)

# -----------------------------------------------------------------------------
# 1. Authentication Endpoints
# -----------------------------------------------------------------------------
@router.post("/auth/login", response_model=Token)
def login(creds: UserLogin):
    user = USERS_DB.get(creds.username)
    if not user or not verify_password(creds.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return Token(
        access_token=token,
        token_type="bearer",
        username=user["username"],
        role=user["role"]
    )

@router.post("/auth/register")
def register(creds: UserRegister):
    if creds.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    role = creds.role if creds.role in ["admin", "analyst", "researcher"] else "analyst"
    USERS_DB[creds.username] = {
        "username": creds.username,
        "password_hash": hash_password(creds.password),
        "role": role,
        "is_active": True
    }
    return {"message": "User registered successfully", "username": creds.username, "role": role}

@router.get("/auth/me", response_model=UserProfile)
def get_profile(user: UserProfile = Depends(get_current_user)):
    return user

# -----------------------------------------------------------------------------
# 2. Dashboard Overview Endpoint
# -----------------------------------------------------------------------------
@router.get("/dashboard")
def get_dashboard_summary():
    data = analytics_engine.get_cached_analytics()
    return {
        "kpi": data.get("kpi"),
        "brand_overview": data.get("brand_analytics")[:6],
        "top_aspects": data.get("aspect_analytics")[:8],
        "recent_complaint_hotspots": data.get("complaint_hotspots")[:6],
        "last_updated": data.get("last_updated")
    }

# -----------------------------------------------------------------------------
# 3. Brand Analytics Endpoint (15 Brands)
# -----------------------------------------------------------------------------
@router.get("/brands")
def get_brands(brand_name: Optional[str] = None):
    data = analytics_engine.get_cached_analytics()
    brands = data.get("brand_analytics", [])
    if brand_name:
        filtered = [b for b in brands if b["brand"].lower() == brand_name.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"Brand '{brand_name}' not found")
        return filtered[0]
    return brands

# -----------------------------------------------------------------------------
# 4. Vehicle Model Analytics & Drill-Down (Pros / Cons / Fixes)
# -----------------------------------------------------------------------------
@router.get("/models")
def get_vehicle_models(brand: Optional[str] = None):
    data = analytics_engine.get_cached_analytics()
    models = data.get("model_drilldown", [])
    if brand:
        models = [m for m in models if m["brand"].lower() == brand.lower()]
    return models

@router.get("/models/drilldown")
def get_model_drilldown(model_name: Optional[str] = None):
    data = analytics_engine.get_cached_analytics()
    models = data.get("model_drilldown", [])
    if model_name:
        filtered = [m for m in models if m["model"].lower() == model_name.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        return filtered[0]
    return models

# -----------------------------------------------------------------------------
# 5. Aspect Taxonomy & Explorer Endpoints (Locked 8 Aspects)
# -----------------------------------------------------------------------------
@router.get("/taxonomy")
def get_taxonomy():
    return {
        "aspect_count": len(AUTOMOTIVE_TAXONOMY),
        "taxonomy": get_taxonomy_summary(),
        "categories": list(AUTOMOTIVE_TAXONOMY.keys())
    }

@router.get("/aspects")
def get_aspects():
    data = analytics_engine.get_cached_analytics()
    return data.get("aspect_analytics", [])

# -----------------------------------------------------------------------------
# 6. Actionable Complaint Hotspots & Recommendations
# -----------------------------------------------------------------------------
@router.get("/complaints")
def get_complaints(brand: Optional[str] = None):
    data = analytics_engine.get_cached_analytics()
    hotspots = data.get("complaint_hotspots", [])
    if brand:
        hotspots = [h for h in hotspots if h["brand"].lower() == brand.lower()]
    return hotspots

@router.get("/recommendations")
def get_recommendations():
    data = analytics_engine.get_cached_analytics()
    hotspots = data.get("complaint_hotspots", [])
    return [
        {
            "brand": h["brand"],
            "model": h["model"],
            "category": h["aspect_category"],
            "complaint_rate_pct": h["complaint_rate_pct"],
            "action": h["recommended_action"]
        }
        for h in hotspots[:10]
    ]

# -----------------------------------------------------------------------------
# 7. Longitudinal Multi-Graph Trends
# -----------------------------------------------------------------------------
@router.get("/trends")
def get_trends():
    data = analytics_engine.get_cached_analytics()
    return data.get("monthly_trends", [])

# -----------------------------------------------------------------------------
# 8. Single Review Sentiment & Aspect Prediction with Explainability
# -----------------------------------------------------------------------------
@router.post("/predict", response_model=PredictResponse)
def predict_sentiment(req: PredictRequest):
    pred = get_predictor(req.model_version or "autosense-tfidf-lr-v1")
    res = pred.predict_review(req.review_text)
    return PredictResponse(**res)

# -----------------------------------------------------------------------------
# 9. Batch Prediction & Auto-Grouping by Brand/Model
# -----------------------------------------------------------------------------
@router.post("/predict/batch")
def predict_batch(req: BatchPredictRequest):
    pred = get_predictor(req.model_version or "autosense-tfidf-lr-v1")
    reviews_list = [item.dict() for item in req.reviews]
    res = pred.predict_batch(reviews_list)
    return res

@router.get("/sample-batch")
def get_sample_batch():
    sample_file = r"V:\BDT\Datasets\batch_test_sample.csv"
    if os.path.exists(sample_file):
        df = pd.read_csv(sample_file)
        return df.to_dict(orient="records")
    return []

# -----------------------------------------------------------------------------
# 10. AutoSense AI Copilot Chatbot Endpoint
# -----------------------------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(req: ChatRequest):
    answer = chatbot.ask(req.message)
    return ChatResponse(**answer)

# -----------------------------------------------------------------------------
# 11. Review Search & Multi-Facet Filtering
# -----------------------------------------------------------------------------
@router.get("/reviews", response_model=ReviewSearchResponse)
def search_reviews(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    sentiment: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    session = get_session()
    query = session.query(Review)
    
    if brand:
        query = query.filter(Review.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(Review.vehicle_model.ilike(f"%{model}%"))
    if sentiment:
        query = query.filter(Review.normalized_sentiment_label == sentiment.lower())
    if keyword:
        query = query.filter(Review.review_text_original.ilike(f"%{keyword}%"))
        
    total_count = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(Review.review_id.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for r in records:
        items.append(ReviewItem(
            review_id=r.review_id,
            source_name=r.source_name,
            brand=r.brand,
            vehicle_model=r.vehicle_model,
            review_text=r.review_text_original,
            rating=r.overall_rating,
            sentiment=r.normalized_sentiment_label,
            date=str(r.review_date) if r.review_date else None
        ))
    session.close()
    
    return ReviewSearchResponse(
        total_matches=total_count,
        page=page,
        page_size=page_size,
        reviews=items
    )

# -----------------------------------------------------------------------------
# 12. Research Benchmarks & Model Evaluation
# -----------------------------------------------------------------------------
@router.get("/research")
def get_research_evaluation():
    registry_path = r"V:\BDT\models\model_registry\model_registry.json"
    bench_path = r"V:\BDT\reports\absa_ground_truth_benchmarks.json"
    
    registry = {}
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            
    benchmarks = {}
    if os.path.exists(bench_path):
        with open(bench_path, 'r', encoding='utf-8') as f:
            benchmarks = json.load(f)
            
    return {
        "model_registry": registry,
        "ground_truth_benchmarks": benchmarks
    }

# -----------------------------------------------------------------------------
# 13. Big Data Pipeline Telemetry
# -----------------------------------------------------------------------------
@router.get("/pipeline")
def get_pipeline_telemetry():
    log_file = r"V:\BDT\bigdata\logs\pipeline_execution_log.json"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"status": "No pipeline runs recorded yet"}
