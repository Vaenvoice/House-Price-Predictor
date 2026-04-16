import sys
import os
from pathlib import Path

# Add the backend directory to sys.path so 'app' can be found
# Root structure: 
# /api/index.py
# /backend/app/...
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
sys.path.append(str(backend_dir))

# Import the FastAPI app instance
from app.main import app
