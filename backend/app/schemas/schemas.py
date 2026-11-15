"""
AutoSense Pydantic Request & Response Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str] = "analyst"

class UserProfile(BaseModel):
    username: str
    role: str
    is_active: bool

class PredictRequest(BaseModel):
    review_text: str = Field(..., min_length=3, example="The engine is powerful and responsive, but mileage is poor.")
    model_version: Optional[str] = "autosense-tfidf-lr-v1"

class AspectDetection(BaseModel):
    category: str
    sentiment: str
    evidence: Optional[str] = None
    matched_keyword: Optional[str] = None
    compound_score: Optional[float] = None

class FeatureAttribution(BaseModel):
    token: str
    weight: float
    direction: str

class ExplainabilityData(BaseModel):
    top_features: List[FeatureAttribution] = []
    supporting_features: List[FeatureAttribution] = []
    opposing_features: List[FeatureAttribution] = []
    explanation_summary: str = ""

class PredictResponse(BaseModel):
    review_text: str
    cleaned_text: str
    predicted_sentiment: str
    confidence: float
    confidence_percentage: float
    probabilities: Dict[str, float]
    explainability: Optional[ExplainabilityData] = None
    aspects_detected: List[AspectDetection] = []
    model_version: str

class BatchReviewItem(BaseModel):
    review_id: Optional[int] = None
    brand: Optional[str] = "Unknown"
    vehicle_model: Optional[str] = "Unknown"
    review_text: str
    rating: Optional[float] = None

class BatchPredictRequest(BaseModel):
    reviews: List[BatchReviewItem]
    model_version: Optional[str] = "autosense-tfidf-lr-v1"

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, example="Which brand has the highest customer rating?")

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    suggestions: List[str] = []

class ReviewItem(BaseModel):
    review_id: int
    source_name: str
    brand: Optional[str]
    vehicle_model: Optional[str]
    review_text: str
    rating: Optional[float]
    sentiment: str
    date: Optional[str]

class ReviewSearchResponse(BaseModel):
    total_matches: int
    page: int
    page_size: int
    reviews: List[ReviewItem]
