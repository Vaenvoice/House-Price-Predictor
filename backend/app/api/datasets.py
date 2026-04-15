"""
EstateAI Dataset API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.dependencies import pipeline
from app.ml.dataset_gen import generate_dataset
from app.ml.preprocessing import parse_uploaded_csv
from app.schemas.schemas import DatasetStats
from app.config import DATASET_PATH
import pandas as pd

router = APIRouter()


@router.get("/dataset")
def get_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    sort_by: str = Query("price", description="Column to sort by"),
    sort_order: str = Query("desc", description="asc or desc"),
    location: str = Query(None, description="Filter by location"),
):
    """Get the dataset with pagination, sorting, and filtering."""
    df = pipeline.load_data()

    # Filter by location
    if location:
        df = df[df["location"] == location]

    # Sort
    ascending = sort_order == "asc"
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    total = len(df)
    total_pages = max(1, (total + page_size - 1) // page_size)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_data = df.iloc[start:end]

    return {
        "data": page_data.to_dict(orient="records"),
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/dataset/stats", response_model=DatasetStats)
def get_dataset_stats():
    """Get summary statistics of the dataset."""
    df = pipeline.load_data()

    return DatasetStats(
        total_rows=len(df),
        columns=df.columns.tolist(),
        area_range=[float(df["area"].min()), float(df["area"].max())],
        price_range=[float(df["price"].min()), float(df["price"].max())],
        age_range=[float(df["age"].min()), float(df["age"].max())],
        room_distribution=df["rooms"].value_counts().to_dict(),
        location_distribution=df["location"].value_counts().to_dict(),
        mean_price=round(float(df["price"].mean()), 2),
        median_price=round(float(df["price"].median()), 2),
    )


@router.post("/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a custom CSV dataset."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()

    try:
        df = parse_uploaded_csv(contents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save uploaded dataset
    df.to_csv(DATASET_PATH, index=False)

    # Retrain models with new data
    pipeline.train()

    return {
        "message": "Dataset uploaded and models retrained",
        "rows": len(df),
        "columns": df.columns.tolist(),
        "best_model": pipeline.best_model_name,
    }


@router.post("/dataset/regenerate")
def regenerate_dataset():
    """Regenerate the synthetic dataset and retrain."""
    df = generate_dataset()
    pipeline.train()

    return {
        "message": "Dataset regenerated and models retrained",
        "rows": len(df),
        "best_model": pipeline.best_model_name,
    }


@router.get("/dataset/distribution")
def get_price_distribution(bins: int = Query(20, ge=5, le=50)):
    """Get price distribution histogram data."""
    df = pipeline.load_data()
    import numpy as np

    counts, bin_edges = np.histogram(df["price"], bins=bins)

    return {
        "counts": counts.tolist(),
        "bin_edges": bin_edges.tolist(),
        "labels": [
            f"{bin_edges[i]/100000:.1f}L - {bin_edges[i+1]/100000:.1f}L"
            for i in range(len(counts))
        ],
    }
