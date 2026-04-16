"""
EstateAI – FastAPI Application Entry Point
Intelligent House Price Prediction Platform
"""
from contextlib import asynccontextmanager
import os
import shutil
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db
from app.dependencies import pipeline
from app.ml.dataset_gen import generate_dataset
from app.config import DATASET_PATH, IS_VERCEL, BUNDLED_DATA_DIR, BUNDLED_MODEL_DIR
from app.api import predictions, models, datasets, analytics, auth


async def initialize_ml_pipeline():
    """Background task to initialize data and train models."""
    await asyncio.sleep(0.1)  # Yield to event loop to allow port binding
    print("\n[Background] Starting ML initialization...")
    try:
        # 1. Generate dataset if missing
        if not DATASET_PATH.exists():
            print("[Background] Generating synthetic dataset (10,000 samples)...")
            generate_dataset()
        else:
            print(f"[Background] Dataset found: {DATASET_PATH}")

        # 2. Load saved models when possible, train only when needed
        force_retrain = os.getenv("FORCE_RETRAIN", "false").lower() in {"1", "true", "yes"}
        loaded = False
        if not force_retrain:
            print("[Background] Loading saved ML models...")
            pipeline.load()
            loaded = pipeline.is_trained and bool(pipeline.models)

        if not loaded:
            if IS_VERCEL:
                print("[Background] Using bundled fallback models for Vercel.")
                pipeline.load(model_dir=BUNDLED_MODEL_DIR)
            else:
                print("[Background] Training ML models...")
                pipeline.train()
                pipeline.warmup()
        else:
            print("[Background] Using cached trained models from disk.")

        print(f"\n[Background] Best model: {pipeline.best_model_name}")
        for name, m in pipeline.metrics.items():
            marker = " *" if name == pipeline.best_model_name else ""
            print(f"   {name}: R2={m['r2_score']:.4f}, RMSE={m['rmse']:,.0f}, MAE={m['mae']:,.0f}{marker}")
        
        print("\n[Background] ML Pipeline is ready!")
    except Exception as e:
        print(f"\n[Background] CRITICAL: Error during background startup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    print("\n===============================================")
    print("   VaenEstate - Intelligent Price Prediction")
    print("===============================================")

    # 1. Initialize database (Fast/Blocking)
    try:
        # On Vercel, copy packaged data/models into writable /tmp.
        if IS_VERCEL:
            bundled_dataset = BUNDLED_DATA_DIR / "synthetic_dataset.csv"
            if bundled_dataset.exists() and not DATASET_PATH.exists():
                DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bundled_dataset, DATASET_PATH)

            if BUNDLED_MODEL_DIR.exists():
                from app.config import MODEL_DIR
                MODEL_DIR.mkdir(parents=True, exist_ok=True)
                for file_path in BUNDLED_MODEL_DIR.glob("*.joblib"):
                    target = MODEL_DIR / file_path.name
                    if not target.exists():
                        shutil.copy2(file_path, target)

        print("Initializing database...")
        init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")

    # 2. Start ML initialization in background to prevent Render timeouts
    asyncio.create_task(initialize_ml_pipeline())

    print("\nVaenEstate is starting up!")
    print("API docs: http://localhost:8000/docs\n")

    yield

    print("\nEstateAI shutting down...")


# Create FastAPI app
app = FastAPI(
    title="EstateAI API",
    description="Intelligent House Price Prediction Platform – AI-powered property valuation for Indian real estate",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(models.router, prefix="/api", tags=["Models"])
app.include_router(datasets.router, prefix="/api", tags=["Datasets"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

@app.get("/api/health", tags=["Health"])
def health_check():
    """Detailed health check for Railway."""
    return {
        "status": "online",
        "models_loaded": pipeline.is_trained,
        "best_model": pipeline.best_model_name
    }

@app.get("/", tags=["Health"])
def root():
    """Root endpoint for basic connectivity check."""
    return {"message": "VaenEstate API Online", "status": "active"}

@app.get("/health", tags=["Health"])
def root_health():
    """Top-level health check."""
    return {"status": "online"}

@app.get("/ping", tags=["Health"])
def ping():
    """Minimal endpoint for Uptime Robot keep-alive."""
    return "pong"

# (Moved to end of file to prevent route shadowing)




# Pre-computed config for speed
from app.config import PRECOMPUTED_LOCATIONS

print(f"DEBUG: PRECOMPUTED_LOCATIONS initialization: {PRECOMPUTED_LOCATIONS is not None} (Type: {type(PRECOMPUTED_LOCATIONS)})")
if PRECOMPUTED_LOCATIONS is None:
    print("CRITICAL: PRECOMPUTED_LOCATIONS is None. Check app/config.py!")

@app.get("/api/locations", tags=["Config"])
def get_locations():
    """Get available locations with metadata."""
    # Robust fallback in case of initialization timing issues
    if PRECOMPUTED_LOCATIONS is not None:
        return PRECOMPUTED_LOCATIONS
    
    # On-demand computation if somehow None
    from app.config import PRECOMPUTED_LOCATIONS as fallback
    if fallback is not None:
        return fallback
        
    return []
