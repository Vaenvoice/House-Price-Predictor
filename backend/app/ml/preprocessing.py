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

    def transform(self, df):
        """Transform new data using fitted preprocessor."""
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit_transform first.")

        df = df.copy()

        # Handle missing values
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].median())
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].fillna(df[col].mode()[0])

        # One-hot encode
        X_encoded = pd.get_dummies(df, columns=["location"], prefix="loc")

        # Add missing columns (locations not in input)
        for col in self.feature_names:
            if col not in X_encoded.columns:
                X_encoded[col] = 0

        # Remove extra columns and enforce order
        X_encoded = X_encoded[self.feature_names]

        # Scale numeric features
        numeric_cols = [c for c in ["area", "rooms", "age"] if c in X_encoded.columns]
        X_encoded[numeric_cols] = self.scaler.transform(X_encoded[numeric_cols])

        return X_encoded.values

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
