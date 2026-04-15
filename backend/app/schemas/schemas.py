"""
VaenEstate Pydantic Schemas
Request/response models for API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Prediction ──────────────────────────────────────────

class PredictionRequest(BaseModel):
    area: float = Field(..., ge=100, le=10000, description="Area in sq ft")
    rooms: int = Field(..., ge=1, le=10, description="Number of rooms")
    location: str = Field(..., description="Location/city name")
    age: float = Field(..., ge=0, le=100, description="Age of house in years")


class Suggestion(BaseModel):
    type: str
    text: str
    impact: float
    direction: str


class Alternative(BaseModel):
    location: str
    price: float
    savings: float


class PredictionInsights(BaseModel):
    market_score: float = Field(..., description="0-100 value score")
    investment_rating: float = Field(..., description="0-5 star rating")
    feature_impact: dict = Field(..., description="Relative contribution of features")
    market_comparison: str = Field(..., description="Text comparing to city average")
    narrative: str = Field(..., description="AI generated explanation")

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence_low: float
    confidence_high: float
    model_used: str
    formatted_price: str
    emi_estimate: Optional[float] = None
    is_outlier: Optional[bool] = False
    alternatives: List[Alternative] = []
    suggestions: List[Suggestion] = []
    insights: Optional[PredictionInsights] = None

PredictionResponse.model_rebuild()


# ── Models / Training ───────────────────────────────────

class ModelMetrics(BaseModel):
    name: str
    rmse: float
    mae: float
    r2_score: float
    is_best: bool = False


class TrainRequest(BaseModel):
    models: Optional[List[str]] = None
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    random_state: int = 42
    rf_n_estimators: int = Field(100, ge=10, le=500)
    rf_max_depth: Optional[int] = Field(None, ge=1, le=50)
    xgb_n_estimators: int = Field(100, ge=10, le=500)
    xgb_learning_rate: float = Field(0.1, ge=0.01, le=1.0)
    xgb_max_depth: int = Field(6, ge=1, le=20)
    ridge_alpha: float = Field(1.0, ge=0.01, le=100.0)
    lasso_alpha: float = Field(1.0, ge=0.01, le=100.0)


class TrainResponse(BaseModel):
    metrics: List[ModelMetrics]
    best_model: str
    feature_importances: dict


# ── Authentication ──────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


# ── Dataset ─────────────────────────────────────────────

class DatasetRow(BaseModel):
    area: float
    rooms: int
    location: str
    age: float
    price: float


class DatasetStats(BaseModel):
    total_rows: int
    columns: List[str]
    area_range: List[float]
    price_range: List[float]
    age_range: List[float]
    room_distribution: dict
    location_distribution: dict
    mean_price: float
    median_price: float


# ── Prediction History ──────────────────────────────────

class PredictionHistory(BaseModel):
    id: int
    area: float
    rooms: int
    location: str
    age: float
    predicted_price: float
    confidence_low: float
    confidence_high: float
    model_used: str
    created_at: str
