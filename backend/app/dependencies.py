"""
EstateAI Shared Dependencies
Singleton instances shared across the application.
"""
from app.ml.pipeline import MLPipeline

# Singleton ML pipeline instance
pipeline = MLPipeline()


def get_pipeline() -> MLPipeline:
    """FastAPI dependency to get the pipeline instance."""
    return pipeline
