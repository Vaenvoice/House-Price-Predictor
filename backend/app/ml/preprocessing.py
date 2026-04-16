"""
EstateAI Data Preprocessing
Handles encoding, scaling, missing values, and CSV upload parsing.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from app.config import MODEL_DIR


class DataPreprocessor:
    """Preprocessor for house price features with fit/transform pattern."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_fitted = False

    def fit_transform(self, df):
        """Fit preprocessor on training data and transform it."""
        df = df.copy()

        # Handle missing values
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].median())
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].fillna(df[col].mode()[0])

        # Separate target
        y = None
        if "price" in df.columns:
            y = df["price"].values
            X = df.drop("price", axis=1)
        else:
            X = df

        # One-hot encode location
        X_encoded = pd.get_dummies(X, columns=["location"], prefix="loc")

        # Store feature names for consistent transform later
        self.feature_names = list(X_encoded.columns)

        # Scale numeric features
        numeric_cols = [c for c in ["area", "rooms", "age"] if c in X_encoded.columns]
        X_encoded[numeric_cols] = self.scaler.fit_transform(X_encoded[numeric_cols])

        self.is_fitted = True
        self.save()

        return X_encoded.values, y, self.feature_names

    def _get_indices(self):
        """Helper to get indices for mapping features fast."""
        indices = {
            "area": -1, "rooms": -1, "age": -1,
            "locations": {}
        }
        for j, fname in enumerate(self.feature_names):
            if fname == "area": indices["area"] = j
            elif fname == "rooms": indices["rooms"] = j
            elif fname == "age": indices["age"] = j
            elif fname.startswith("loc_"):
                indices["locations"][fname[4:]] = j
        return indices

    def transform(self, data):
        """Transform new data efficiently with batching and pre-calculated indices."""
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit_transform first.")

        # Handle both single dict and list of dicts
        samples = [data] if isinstance(data, dict) else data
        num_samples = len(samples)
        num_features = len(self.feature_names)
        X_encoded = np.zeros((num_samples, num_features))
        
        # Get indices once
        idx = self._get_indices()

        # Extract numeric values for batch scaling
        numeric_matrix = np.zeros((num_samples, 3))
        for i, sample in enumerate(samples):
            numeric_matrix[i, 0] = sample.get("area", 1200)
            numeric_matrix[i, 1] = sample.get("rooms", 2)
            numeric_matrix[i, 2] = sample.get("age", 5)

        # Batch Scale
        scaled_matrix = self.scaler.transform(numeric_matrix)

        # Map to encoded matrix
        for i, sample in enumerate(samples):
            # 1. Fill base numeric features
            if idx["area"] != -1: X_encoded[i, idx["area"]] = scaled_matrix[i, 0]
            if idx["rooms"] != -1: X_encoded[i, idx["rooms"]] = scaled_matrix[i, 1]
            if idx["age"] != -1: X_encoded[i, idx["age"]] = scaled_matrix[i, 2]
            
            # 2. Fill location
            location = sample.get("location", "Mumbai")
            loc_idx = idx["locations"].get(location)
            if loc_idx is not None:
                X_encoded[i, loc_idx] = 1.0

        return X_encoded

    def save(self):
        """Persist preprocessor state to disk."""
        joblib.dump(
            {"scaler": self.scaler, "feature_names": self.feature_names},
            MODEL_DIR / "preprocessor.joblib",
        )

    def load(self):
        """Load preprocessor state from disk."""
        data = joblib.load(MODEL_DIR / "preprocessor.joblib")
        self.scaler = data["scaler"]
        self.feature_names = data["feature_names"]
        self.is_fitted = True


def parse_uploaded_csv(file_bytes):
    """Parse and validate an uploaded CSV file."""
    import io

    df = pd.read_csv(io.BytesIO(file_bytes))

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Validate required columns
    required = {"area", "rooms", "location", "age", "price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Clean data types
    df["area"] = pd.to_numeric(df["area"], errors="coerce")
    df["rooms"] = pd.to_numeric(df["rooms"], errors="coerce").astype("Int64")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Drop rows where all key fields are null
    df = df.dropna(subset=["area", "price"])

    return df
