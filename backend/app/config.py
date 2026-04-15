"""
VaenEstate Configuration
Central configuration for paths, locations, and application settings.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLED_DATA_DIR = BASE_DIR / "data"

# Runtime environment
IS_VERCEL = os.getenv("VERCEL", "").lower() in {"1", "true", "yes"}

# Data directory (Vercel serverless filesystem is writable under /tmp only)
if IS_VERCEL:
    DATA_DIR = Path("/tmp") / "vaenestate_data"
else:
    DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Model directory
MODEL_DIR = DATA_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)
BUNDLED_MODEL_DIR = BUNDLED_DATA_DIR / "models"

# Database
DB_PATH = DATA_DIR / "estateai.db"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "vaenestate-jwt-secret-key-2026-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Dataset Configuration
DATASET_SIZE = 50000
DATASET_PATH = DATA_DIR / "synthetic_dataset.csv"

# Indian City Locations with pricing multipliers and coordinates
LOCATIONS = {
    "Mumbai": {"type": "tier-1", "multiplier": 2.5, "lat": 19.0760, "lng": 72.8777, "label": "Mumbai, Maharashtra"},
    "Delhi": {"type": "tier-1", "multiplier": 2.2, "lat": 28.7041, "lng": 77.1025, "label": "New Delhi"},
    "Bangalore": {"type": "tier-1", "multiplier": 2.0, "lat": 12.9716, "lng": 77.5946, "label": "Bangalore, Karnataka"},
    "Hyderabad": {"type": "tier-1", "multiplier": 1.6, "lat": 17.3850, "lng": 78.4867, "label": "Hyderabad, Telangana"},
    "Pune": {"type": "tier-1", "multiplier": 1.5, "lat": 18.5204, "lng": 73.8567, "label": "Pune, Maharashtra"},
    "Chennai": {"type": "tier-1", "multiplier": 1.4, "lat": 13.0827, "lng": 80.2707, "label": "Chennai, Tamil Nadu"},
    "Kolkata": {"type": "tier-2", "multiplier": 1.2, "lat": 22.5726, "lng": 88.3639, "label": "Kolkata, West Bengal"},
    "Ahmedabad": {"type": "tier-2", "multiplier": 1.1, "lat": 23.0225, "lng": 72.5714, "label": "Ahmedabad, Gujarat"},
    "Jaipur": {"type": "tier-2", "multiplier": 0.9, "lat": 26.9124, "lng": 75.7873, "label": "Jaipur, Rajasthan"},
    "Gurgaon": {"type": "tier-1", "multiplier": 2.1, "lat": 28.4595, "lng": 77.0266, "label": "Gurgaon, Haryana"},
    "Noida": {"type": "tier-1", "multiplier": 1.9, "lat": 28.5355, "lng": 77.3910, "label": "Noida, Uttar Pradesh"},
    "Chandigarh": {"type": "tier-2", "multiplier": 1.8, "lat": 30.7333, "lng": 76.7794, "label": "Chandigarh"},
    "Lucknow": {"type": "tier-2", "multiplier": 1.3, "lat": 26.8467, "lng": 80.9462, "label": "Lucknow, UP"},
    "Kochi": {"type": "tier-2", "multiplier": 1.4, "lat": 9.9312, "lng": 76.2673, "label": "Kochi, Kerala"},
    "Indore": {"type": "tier-2", "multiplier": 1.2, "lat": 22.7196, "lng": 75.8577, "label": "Indore, MP"},
    "Surat": {"type": "tier-2", "multiplier": 1.4, "lat": 21.1702, "lng": 72.8311, "label": "Surat, Gujarat"},
    "Coimbatore": {"type": "tier-2", "multiplier": 1.3, "lat": 11.0168, "lng": 76.9558, "label": "Coimbatore, TN"},
    "Nagpur": {"type": "tier-2", "multiplier": 1.2, "lat": 21.1458, "lng": 79.0882, "label": "Nagpur, Maharashtra"},
    "Vadodara": {"type": "tier-2", "multiplier": 1.2, "lat": 22.3072, "lng": 73.1812, "label": "Vadodara, Gujarat"},
    "Bhopal": {"type": "tier-2", "multiplier": 1.1, "lat": 23.2599, "lng": 77.4126, "label": "Bhopal, MP"},
    "Ludhiana": {"type": "tier-2", "multiplier": 1.1, "lat": 30.9010, "lng": 75.8573, "label": "Ludhiana, Punjab"},
    "Visakhapatnam": {"type": "tier-2", "multiplier": 1.3, "lat": 17.6868, "lng": 83.2185, "label": "Vizag, Andhra"},
    "Agra": {"type": "tier-3", "multiplier": 1.0, "lat": 27.1767, "lng": 78.0081, "label": "Agra, UP"},
    "Nashik": {"type": "tier-2", "multiplier": 1.1, "lat": 19.9975, "lng": 73.7898, "label": "Nashik, Maharashtra"},
    "Madurai": {"type": "tier-3", "multiplier": 1.0, "lat": 9.9252, "lng": 78.1198, "label": "Madurai, TN"},
    "Varanasi": {"type": "tier-3", "multiplier": 1.1, "lat": 25.3176, "lng": 82.9739, "label": "Varanasi, UP"},
    "Rajkot": {"type": "tier-3", "multiplier": 1.0, "lat": 22.3039, "lng": 70.8022, "label": "Rajkot, Gujarat"},
    "Jamshedpur": {"type": "tier-2", "multiplier": 1.0, "lat": 22.8046, "lng": 86.2029, "label": "Jamshedpur, Jharkhand"},
    "Srinagar": {"type": "tier-3", "multiplier": 1.0, "lat": 34.0837, "lng": 74.7973, "label": "Srinagar, J&K"},
    "Amritsar": {"type": "tier-3", "multiplier": 1.0, "lat": 31.6340, "lng": 74.8723, "label": "Amritsar, Punjab"},
    "Jodhpur": {"type": "tier-3", "multiplier": 0.9, "lat": 26.2389, "lng": 73.0243, "label": "Jodhpur, Rajasthan"},
    "Raipur": {"type": "tier-3", "multiplier": 0.9, "lat": 21.2514, "lng": 81.6296, "label": "Raipur, Chhattisgarh"},
    "Bhubaneswar": {"type": "tier-2", "multiplier": 1.1, "lat": 20.2961, "lng": 85.8245, "label": "Bhubaneswar, Odisha"},
    "Guwahati": {"type": "tier-2", "multiplier": 1.0, "lat": 26.1445, "lng": 91.7362, "label": "Guwahati, Assam"},
    "Mysore": {"type": "tier-3", "multiplier": 1.1, "lat": 12.2958, "lng": 76.6394, "label": "Mysore, Karnataka"},
    "Dehradun": {"type": "tier-3", "multiplier": 1.1, "lat": 30.3165, "lng": 78.0322, "label": "Dehradun, Uttarakhand"},
    "Shimla": {"type": "tier-3", "multiplier": 1.2, "lat": 31.1048, "lng": 77.1734, "label": "Shimla, HP"},
    "Vijayawada": {"type": "tier-2", "multiplier": 1.1, "lat": 16.5062, "lng": 80.6480, "label": "Vijayawada, Andhra"},
    "Pondicherry": {"type": "tier-3", "multiplier": 1.0, "lat": 11.9416, "lng": 79.8083, "label": "Pondicherry"},
    "Udaipur": {"type": "tier-3", "multiplier": 0.9, "lat": 24.5854, "lng": 73.7125, "label": "Udaipur, Rajasthan"},
    "Mangalore": {"type": "tier-3", "multiplier": 1.1, "lat": 12.9141, "lng": 74.8560, "label": "Mangalore, Karnataka"},
    "Ranchi": {"type": "tier-3", "multiplier": 0.9, "lat": 23.3441, "lng": 85.3096, "label": "Ranchi, Jharkhand"},
    "Patna": {"type": "tier-3", "multiplier": 1.1, "lat": 25.5941, "lng": 85.1376, "label": "Patna, Bihar"},
    "Hubli": {"type": "tier-3", "multiplier": 0.8, "lat": 15.3647, "lng": 75.1240, "label": "Hubli, Karnataka"},
    "Warangal": {"type": "tier-3", "multiplier": 0.8, "lat": 18.0000, "lng": 79.5800, "label": "Warangal, Telangana"},
    "Guntur": {"type": "tier-3", "multiplier": 0.9, "lat": 16.3067, "lng": 80.4365, "label": "Guntur, Andhra"},
    "Tiruchi": {"type": "tier-3", "multiplier": 0.9, "lat": 10.7905, "lng": 78.7047, "label": "Tiruchirappalli, TN"},
    "Salem": {"type": "tier-3", "multiplier": 0.9, "lat": 11.6643, "lng": 78.1460, "label": "Salem, TN"},
    "Bareilly": {"type": "tier-3", "multiplier": 0.8, "lat": 28.3670, "lng": 79.4304, "label": "Bareilly, UP"},
    "Aligarh": {"type": "tier-3", "multiplier": 0.8, "lat": 27.8936, "lng": 78.0883, "label": "Aligarh, UP"},
    "Suburban": {"type": "suburban", "multiplier": 0.7, "lat": 19.2183, "lng": 72.9781, "label": "Suburban Area"},
    "Rural": {"type": "rural", "multiplier": 0.4, "lat": 20.5937, "lng": 78.9629, "label": "Rural Area"},
}

LOCATION_NAMES = list(LOCATIONS.keys())
