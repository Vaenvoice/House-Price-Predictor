"""
VaenEstate ML Training Pipeline
Trains, compares, and manages multiple regression models.
"""
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
try:
    import pandas as pd
except ImportError:
    pd = None

from app.config import MODEL_DIR, DATASET_PATH
from app.ml.preprocessing import DataPreprocessor
from app.ml.dataset_gen import generate_dataset


class MLPipeline:
    """Complete ML pipeline for house price prediction."""

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.models = {}
        self.metrics = {}
        self.best_model_name = None
        self.feature_importances = {}
        self.is_trained = False

    def load_data(self, csv_path=None):
        """Load dataset from CSV or generate if missing."""
        if pd is None:
            print("Warning: Pandas not available. Dataset loading skipped.")
            return None
        if csv_path:
            return pd.read_csv(csv_path)
        if DATASET_PATH.exists():
            return pd.read_csv(DATASET_PATH)
        return generate_dataset()

    def train(self, params=None):
        """Train all models and auto-select the best one."""
        if params is None:
            params = {}

        # Reset state to avoid stale metrics/models on retraining.
        self.models = {}
        self.metrics = {}
        self.feature_importances = {}
        self.best_model_name = None

        df = self.load_data(params.get("csv_path"))

        test_size = params.get("test_size", 0.2)
        random_state = params.get("random_state", 42)

        # Preprocess
        X, y, feature_names = self.preprocessor.fit_transform(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Define model configurations
        model_configs = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=params.get("ridge_alpha", 1.0)),
            "Lasso Regression": Lasso(alpha=params.get("lasso_alpha", 1.0)),
            "Random Forest": RandomForestRegressor(
                n_estimators=params.get("rf_n_estimators", 100),
                max_depth=params.get("rf_max_depth", None),
                random_state=random_state,
                n_jobs=-1,
            ),
            "Gradient Boosting": HistGradientBoostingRegressor(
                max_iter=params.get("xgb_n_estimators", 100),
                learning_rate=params.get("xgb_learning_rate", 0.1),
                max_depth=params.get("xgb_max_depth", 6),
                random_state=random_state,
            ),
        }

        # Filter models if specific ones requested
        selected = params.get("models")
        if selected:
            model_configs = {k: v for k, v in model_configs.items() if k in selected}

        best_r2 = -float("inf")

        for name, model in model_configs.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Calculate metrics
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            mae = float(mean_absolute_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))

            self.models[name] = model
            self.metrics[name] = {
                "rmse": round(rmse, 2),
                "mae": round(mae, 2),
                "r2_score": round(r2, 4),
            }

            # Extract feature importance
            if hasattr(model, "feature_importances_"):
                self.feature_importances[name] = dict(
                    zip(feature_names, model.feature_importances_.tolist())
                )
            elif hasattr(model, "coef_"):
                importance = np.abs(model.coef_)
                total = importance.sum()
                if total > 0:
                    importance = importance / total
                self.feature_importances[name] = dict(
                    zip(feature_names, importance.tolist())
                )

            # Track best model
            if r2 > best_r2:
                best_r2 = r2
                self.best_model_name = name

            # Save individual model
            model_filename = name.lower().replace(" ", "_") + ".joblib"
            joblib.dump(model, MODEL_DIR / model_filename)

        self.is_trained = True

        # Pre-compute analytics summary for Pandas-free runtime
        summary = {}
        if df is not None:
            summary = {
                "total_samples": len(df),
                "avg_price": float(df["price"].mean()),
                "median_price": float(df["price"].median()),
                "price_std": float(df["price"].std()),
                "avg_area": float(df["area"].mean()),
                "avg_age": float(df["age"].mean()),
                "num_locations": df["location"].nunique(),
            }

        # Save pipeline state
        joblib.dump(
            {
                "best_model_name": self.best_model_name,
                "metrics": self.metrics,
                "feature_importances": self.feature_importances,
                "analytics_summary": summary,
                "location_stats": self.get_location_stats() if df is not None else []
            },
            MODEL_DIR / "pipeline_state.joblib",
        )

        print(f"  Best model: {self.best_model_name} (R2 = {best_r2:.4f})")
        return self.metrics

    def _predict_core(self, area, rooms, location, age):
        """Run a single-model inference without extra derived sections."""
        if not self.is_trained:
            self.load()

        input_data = {"area": area, "rooms": rooms, "location": location, "age": age}
        X = self.preprocessor.transform(input_data)
        model = self.models[self.best_model_name]
        prediction = float(model.predict(X)[0])

        # Confidence range from ensemble variance
        all_predictions = []
        for name, m in self.models.items():
            try:
                pred = float(m.predict(X)[0])
                all_predictions.append(pred)
            except Exception:
                pass

        if len(all_predictions) > 1:
            std = np.std(all_predictions)
            confidence_low = max(0, prediction - 1.96 * std)
            confidence_high = prediction + 1.96 * std
        else:
            confidence_low = prediction * 0.85
            confidence_high = prediction * 1.15

        # Financial ROI - Estimated EMI
        loan_amount = prediction * 0.8  # 80% LTV
        monthly_rate = 0.085 / 12
        num_months = 240
        emi = (loan_amount * monthly_rate * (1 + monthly_rate)**num_months) / ((1 + monthly_rate)**num_months - 1)

        # Outlier Detection
        is_outlier = bool(area < 400 or area > 6000 or rooms > 8 or age > 60)

        # Formatting
        if prediction < 10000000:
            formatted = f"₹{prediction/100000:.1f}L"
        else:
            formatted = f"₹{prediction/10000000:.2f}Cr"

        return {
            "predicted_price": round(prediction, -3),
            "formatted_price": formatted,
            "confidence_low": round(max(0, confidence_low), -3),
            "confidence_high": round(confidence_high, -3),
            "model_used": self.best_model_name,
            "emi_estimate": round(emi, 0),
            "is_outlier": is_outlier,
        }

    def predict(self, area, rooms, location, age):
        """Run prediction using the best model."""
        result = self._predict_core(area, rooms, location, age)
        result["alternatives"] = self.get_market_alternatives(area, rooms, location, age)
        return result

    def get_market_alternatives(self, area, rooms, current_location, age):
        """Find 'Better Value' properties in similar or cheaper tiers."""
        from app.config import LOCATIONS
        current_info = LOCATIONS.get(current_location, {"multiplier": 1.0, "type": "tier-2"})
        current_mult = current_info["multiplier"]
        
        alternatives = []
        # Look for locations with lower multiplier but same or better 'type'
        for loc_name, info in LOCATIONS.items():
            if loc_name == current_location: continue
            
            # If it's cheaper by at least 15%
            if info["multiplier"] < current_mult * 0.85:
                pred = self._predict_core(area, rooms, loc_name, age)
                alternatives.append({
                    "location": loc_name,
                    "price": pred["predicted_price"],
                    "savings": round(current_mult * 100 - info["multiplier"] * 100, 1),
                    "type": info["type"]
                })
        
        # Return top 3 best savings
        return sorted(alternatives, key=lambda x: x["savings"], reverse=True)[:3]

    def get_suggestions(self, area, rooms, location, age):
        """Generate AI suggestions for price optimization."""
        base = self._predict_core(area, rooms, location, age)
        suggestions = []

        # Area increase suggestion
        if area + 200 <= 5000:
            more_area = self._predict_core(area + 200, rooms, location, age)
            diff = more_area["predicted_price"] - base["predicted_price"]
            suggestions.append(
                {
                    "type": "area",
                    "text": "Increasing area by 200 sq ft",
                    "impact": diff,
                    "direction": "up" if diff > 0 else "down",
                }
            )

        # Extra room suggestion
        if rooms < 6:
            more_rooms = self._predict_core(area, rooms + 1, location, age)
            diff = more_rooms["predicted_price"] - base["predicted_price"]
            suggestions.append(
                {
                    "type": "rooms",
                    "text": "Adding 1 more room",
                    "impact": diff,
                    "direction": "up" if diff > 0 else "down",
                }
            )

        # Newer construction suggestion
        if age > 5:
            newer = self._predict_core(area, rooms, location, max(0, age - 5))
            diff = newer["predicted_price"] - base["predicted_price"]
            suggestions.append(
                {
                    "type": "age",
                    "text": "5 years newer construction",
                    "impact": diff,
                    "direction": "up" if diff > 0 else "down",
                }
            )

        # Better location suggestion
        from app.config import LOCATIONS

        current_mult = LOCATIONS.get(location, {}).get("multiplier", 1.0)
        better_locations = sorted(
            [(k, v) for k, v in LOCATIONS.items() if v["multiplier"] > current_mult],
            key=lambda x: x[1]["multiplier"],
        )
        if better_locations:
            best_loc_name, best_loc_info = better_locations[0]
            loc_pred = self._predict_core(area, rooms, best_loc_name, age)
            diff = loc_pred["predicted_price"] - base["predicted_price"]
            suggestions.append(
                {
                    "type": "location",
                    "text": f"Moving to {best_loc_name}",
                    "impact": diff,
                    "direction": "up" if diff > 0 else "down",
                }
            )

        return suggestions

    def get_advanced_insights(self, area, rooms, location, age):
        """Generate high-fidelity AI insights for a specific property."""
        base_prediction = self._predict_core(area, rooms, location, age)
        current_price = base_prediction["predicted_price"]
        current_ppsf = current_price / area

        # 1. Market Comparison
        all_stats = self.get_location_stats()
        loc_stats = next((s for s in all_stats if s["location"] == location), None)
        
        avg_ppsf = 3500 * 1.5 # Default fallback
        if loc_stats:
            avg_ppsf = loc_stats["avg_price"] / loc_stats["avg_area"]
        
        ppsf_diff = ((current_ppsf - avg_ppsf) / avg_ppsf) * 100
        comparison = f"{abs(ppsf_diff):.1f}% {'above' if ppsf_diff > 0 else 'below'} city average"
        
        # 2. Market Score (0-100) - Higher is better value
        # Good value if price/sqft is lower than average
        score = 50 - (ppsf_diff * 0.5) 
        score = max(5, min(95, score + 20)) # Normalize to 0-100 range, bias towards positive

        # 3. Investment Rating (0-5)
        from app.config import LOCATIONS
        tier = LOCATIONS.get(location, {}).get("type", "tier-3")
        tier_bonus = 1.0 if tier == "tier-1" else 0.5 if tier == "tier-2" else 0.2
        
        # Rating factors: Tier + Value + Age (newer is better)
        rating = 2.0 + tier_bonus
        if ppsf_diff < 0: rating += 1.0 # Good value bonus
        if age < 5: rating += 0.5 # New construction bonus
        elif age > 20: rating -= 0.5 # Depreciation penalty
        
        rating = max(1.0, min(5.0, rating))

        # 4. Local Feature Impact (simplified SHAP)
        # We perturb each feature to see direction and magnitude
        impacts = {}
        
        # Area Impact
        p_area = self._predict_core(area * 1.1, rooms, location, age)["predicted_price"]
        impacts["area"] = (p_area - current_price) / current_price
        
        # Room Impact
        p_rooms = self._predict_core(area, min(6, rooms + 1), location, age)["predicted_price"]
        impacts["rooms"] = (p_rooms - current_price) / current_price
        
        # Age Impact
        p_age = self._predict_core(area, rooms, location, max(0, age - 5))["predicted_price"]
        impacts["age"] = (p_age - current_price) / current_price
        
        # Location Impact (compared to Rural)
        p_loc = self._predict_core(area, rooms, "Rural", age)["predicted_price"]
        impacts["location"] = (current_price - p_loc) / current_price

        # Normalize impacts for visualization
        total = sum(abs(v) for v in impacts.values())
        if total > 0:
            impacts = {k: round(v / total, 3) for k, v in impacts.items()}

        # 5. Narrative Generation
        narratives = []
        if tier == "tier-1":
            narratives.append(f"{location} is a high-growth Tier 1 hub, providing strong price support.")
        if ppsf_diff < -10:
            narratives.append("Current pricing represents a significant value-buy opportunity.")
        elif ppsf_diff > 10:
            narratives.append("Property is priced at a premium compared to neighborhood averages.")
        
        if age < 3:
            narratives.append("Modern construction significantly enhances liquidity and resale value.")
        elif age > 25:
            narratives.append("Asset age is a primary depreciation factor; renovation may unlock value.")
            
        if not narratives:
            narratives.append("Stable market performance with balanced pricing drivers.")

        return {
            "market_score": round(score, 1),
            "investment_rating": round(rating, 1),
            "feature_impact": impacts,
            "market_comparison": comparison,
            "narrative": " ".join(narratives)
        }

    def load(self):
        """Load trained models and state from disk."""
        try:
            state = joblib.load(MODEL_DIR / "pipeline_state.joblib")
            self.best_model_name = state["best_model_name"]
            self.metrics = state["metrics"]
            self.feature_importances = state["feature_importances"]

            self.preprocessor.load()
            
            # Load pre-computed state
            self.analytics_summary = state.get("analytics_summary", {})
            self.location_stats = state.get("location_stats", [])
            self.correlation_data = state.get("correlation_data", {"columns": [], "data": []})

            for name in self.metrics.keys():
                model_file = MODEL_DIR / (name.lower().replace(" ", "_") + ".joblib")
                if model_file.exists():
                    self.models[name] = joblib.load(model_file)

            self.is_trained = True
            print(f"  Loaded {len(self.models)} models from disk")
        except Exception as e:
            print(f"  No saved models found: {e}")
            self.is_trained = False

    def get_correlation_data(self):
        """Return correlation matrix – use pre-computed if on Vercel."""
        if hasattr(self, 'correlation_data'):
            return self.correlation_data
            
        df = self.load_data()
        if df is None: return {"columns": [], "data": []}
        
        numeric_df = df.select_dtypes(include=[np.number])
        corr = numeric_df.corr()
        return {"columns": corr.columns.tolist(), "data": corr.values.tolist()}

    def get_scatter_data(self, x_col="area", y_col="price", sample_size=500):
        """Return scatter plot data – requires Pandas (local only)."""
        df = self.load_data()
        if df is None: return {"x": [], "y": [], "labels": []}
        
        if len(df) > sample_size:
            df = df.sample(sample_size, random_state=42)
        return {
            "x": df[x_col].tolist(),
            "y": df[y_col].tolist(),
            "labels": df["location"].tolist() if "location" in df.columns else None,
        }

    def get_location_stats(self):
        """Return pricing statistics – use pre-computed if on Vercel."""
        if hasattr(self, 'location_stats') and self.location_stats:
            return self.location_stats
            
        df = self.load_data()
        if df is None: return []
        
        stats = []
        for location in df["location"].unique():
            loc_df = df[df["location"] == location]
            stats.append(
                {
                    "location": location,
                    "avg_price": round(loc_df["price"].mean(), 2),
                    "median_price": round(loc_df["price"].median(), 2),
                    "min_price": round(loc_df["price"].min(), 2),
                    "max_price": round(loc_df["price"].max(), 2),
                    "count": len(loc_df),
                    "avg_area": round(loc_df["area"].mean(), 2),
                    "avg_age": round(loc_df["age"].mean(), 2),
                }
            )
        stats.sort(key=lambda x: x["avg_price"], reverse=True)
        return stats
