"""
VaenEstate Prediction API Endpoints
"""
from fastapi import APIRouter, HTTPException
from app.dependencies import pipeline
from app.database import get_connection
from app.schemas.schemas import PredictionRequest, PredictionResponse, PredictionHistory
from app.config import LOCATION_NAMES
from typing import List
from functools import lru_cache

router = APIRouter()

# Cached helper for prediction results
@lru_cache(maxsize=128)
def get_cached_prediction(area: int, rooms: int, location: str, age: int):
    """Heavy computation helper with LRU cache."""
    result = pipeline.predict(area, rooms, location, age)
    suggestions = pipeline.get_suggestions(area, rooms, location, age)
    insights = pipeline.get_advanced_insights(area, rooms, location, age)
    return result, suggestions, insights


def format_inr(amount):
    """Format number as Indian Rupee string."""
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount / 100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


@router.post("/predict", response_model=PredictionResponse)
def predict_price(req: PredictionRequest):
    """Predict house price based on input features."""
    if not pipeline.is_trained:
        raise HTTPException(status_code=503, detail="Models not trained yet")

    if req.location not in LOCATION_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Choose from: {LOCATION_NAMES}",
        )

    # Retrieve from cache or compute
    result, suggestions, insights = get_cached_prediction(
        req.area, req.rooms, req.location, req.age
    )

    # Save to database
    try:
        conn = get_connection()
        conn.execute(
            """INSERT INTO predictions (area, rooms, location, age, predicted_price,
               confidence_low, confidence_high, model_used)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                req.area,
                req.rooms,
                req.location,
                req.age,
                result["predicted_price"],
                result["confidence_low"],
                result["confidence_high"],
                result["model_used"],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not save prediction: {e}")

    return PredictionResponse(
        predicted_price=result["predicted_price"],
        confidence_low=result["confidence_low"],
        confidence_high=result["confidence_high"],
        model_used=result["model_used"],
        formatted_price=format_inr(result["predicted_price"]),
        suggestions=suggestions,
        insights=insights,
    )


@router.get("/predictions/history", response_model=List[PredictionHistory])
def get_prediction_history(limit: int = 50):
    """Get past predictions, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()

    return [
        PredictionHistory(
            id=row["id"],
            area=row["area"],
            rooms=row["rooms"],
            location=row["location"],
            age=row["age"],
            predicted_price=row["predicted_price"],
            confidence_low=row["confidence_low"] or 0,
            confidence_high=row["confidence_high"] or 0,
            model_used=row["model_used"] or "",
            created_at=row["created_at"] or "",
        )
        for row in rows
    ]


@router.delete("/predictions/history")
def clear_prediction_history():
    """Clear all prediction history."""
    conn = get_connection()
    conn.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
    return {"message": "Prediction history cleared"}
