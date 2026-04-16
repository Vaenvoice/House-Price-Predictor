"""
VaenEstate Analytics API Endpoints
"""
from fastapi import APIRouter
from app.dependencies import pipeline
from app.config import LOCATIONS

router = APIRouter()


@router.get("/analytics/correlation")
def get_correlation():
    """Get correlation matrix for numeric features."""
    if not pipeline.is_trained:
        return {"columns": [], "data": []}
    return pipeline.get_correlation_data()


@router.get("/analytics/scatter")
def get_scatter(x: str = "area", y: str = "price", sample: int = 500):
    """Get scatter plot data for two variables."""
    return pipeline.get_scatter_data(x_col=x, y_col=y, sample_size=sample)


@router.get("/analytics/location-pricing")
def get_location_pricing():
    """Get pricing stats grouped by location with coordinates."""
    stats = pipeline.get_location_stats()

    # Enrich with location metadata
    for stat in stats:
        loc_info = LOCATIONS.get(stat["location"], {})
        stat["lat"] = loc_info.get("lat", 0)
        stat["lng"] = loc_info.get("lng", 0)
        stat["type"] = loc_info.get("type", "unknown")
        stat["label"] = loc_info.get("label", stat["location"])

    return stats


@router.get("/analytics/summary")
def get_analytics_summary():
    """Get a high-level analytics summary."""
    if not pipeline.is_trained:
        return {"status": "not_trained"}

    # Use pre-computed summary to avoid Pandas runtime dependency
    summary = getattr(pipeline, "analytics_summary", {})
    
    # Fallback: if summary is missing but we are "trained", 
    # it might be a legacy state file or a fresh training in progress
    if not summary:
        # Check if we can compute it on the fly (might be slow but better than empty)
        try:
            df = pipeline.load_data()
            if df is not None:
                summary = {
                    "total_samples": len(df),
                    "avg_price": float(df["price"].mean()),
                    "best_r2": pipeline.metrics.get(pipeline.best_model_name, {}).get("r2_score", 0),
                }
                pipeline.analytics_summary = summary
        except Exception:
            return {"status": "summary_missing"}

    return {
        "total_samples": summary.get("total_samples", 0),
        "avg_price": summary.get("avg_price", 0),
        "best_model": pipeline.best_model_name,
        "best_r2": summary.get("best_r2") or pipeline.metrics.get(pipeline.best_model_name, {}).get(
            "r2_score", 0
        ),
        "models_trained": len(pipeline.metrics),
        "status": "ready"
    }
