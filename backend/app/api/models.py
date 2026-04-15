"""
EstateAI Model Management API Endpoints
"""
from fastapi import APIRouter
from app.dependencies import pipeline
from app.schemas.schemas import TrainRequest, TrainResponse, ModelMetrics
from typing import List

router = APIRouter()


@router.get("/models/comparison", response_model=List[ModelMetrics])
def get_model_comparison():
    """Get metrics for all trained models."""
    if not pipeline.is_trained:
        return []

    results = []
    for name, metrics in pipeline.metrics.items():
        results.append(
            ModelMetrics(
                name=name,
                rmse=metrics["rmse"],
                mae=metrics["mae"],
                r2_score=metrics["r2_score"],
                is_best=(name == pipeline.best_model_name),
            )
        )

    results.sort(key=lambda x: x.r2_score, reverse=True)
    return results


@router.get("/models/feature-importance")
def get_feature_importance():
    """Get feature importance from the best model."""
    if not pipeline.is_trained or not pipeline.feature_importances:
        return {"features": [], "importances": {}}

    return {
        "importances": pipeline.feature_importances,
        "best_model": pipeline.best_model_name,
    }


@router.post("/models/train", response_model=TrainResponse)
def train_models(req: TrainRequest):
    """Retrain models with custom hyperparameters."""
    params = {
        "models": req.models,
        "test_size": req.test_size,
        "random_state": req.random_state,
        "rf_n_estimators": req.rf_n_estimators,
        "rf_max_depth": req.rf_max_depth,
        "xgb_n_estimators": req.xgb_n_estimators,
        "xgb_learning_rate": req.xgb_learning_rate,
        "xgb_max_depth": req.xgb_max_depth,
        "ridge_alpha": req.ridge_alpha,
        "lasso_alpha": req.lasso_alpha,
    }

    pipeline.train(params)

    metrics_list = []
    for name, metrics in pipeline.metrics.items():
        metrics_list.append(
            ModelMetrics(
                name=name,
                rmse=metrics["rmse"],
                mae=metrics["mae"],
                r2_score=metrics["r2_score"],
                is_best=(name == pipeline.best_model_name),
            )
        )

    return TrainResponse(
        metrics=metrics_list,
        best_model=pipeline.best_model_name,
        feature_importances=pipeline.feature_importances,
    )


@router.get("/models/best")
def get_best_model():
    """Get info about the current best model."""
    if not pipeline.is_trained:
        return {"name": None, "metrics": None}

    return {
        "name": pipeline.best_model_name,
        "metrics": pipeline.metrics.get(pipeline.best_model_name),
    }
