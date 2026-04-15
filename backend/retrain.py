import os
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ml.dataset_gen import generate_dataset
from app.ml.pipeline import MLPipeline
from app.config import DATASET_PATH

def main():
    print("--- VaenEstate Retraining Tool ---")
    
    # Force delete existing dataset to trigger regeneration
    if DATASET_PATH.exists():
        print(f"Removing old dataset: {DATASET_PATH}")
        os.remove(DATASET_PATH)
    
    print("\n1. Generating new expanded dataset (50,000 samples)...")
    generate_dataset()
    
    print("\n2. Initializing ML Pipeline...")
    pipeline = MLPipeline()
    
    print("\n3. Training models on new data...")
    metrics = pipeline.train()
    
    print("\n--- Training Complete ---")
    print(f"Best Model: {pipeline.best_model_name}")
    for name, m in metrics.items():
        print(f"  {name}: R2={m['r2_score']:.4f}")

if __name__ == "__main__":
    main()
