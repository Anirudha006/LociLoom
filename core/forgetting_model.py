"""
LociLoom Forgetting Predictor and Memory Retention Estimator
Predicts the probability that a student will forget a concept at their next review.
Features:
- days_since_last_review, num_reviews, past_accuracy, avg_response_time,
  difficulty, hints_used, topic, time_of_day
Models: Logistic Regression vs Gradient Boosting, compared with Fixed-Interval Baseline.
Projects forgetting probabilities across 24h, 3-day, and 7-day horizons.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "forgetting_model.joblib")
SEED_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "recall_logs_seed.csv")

DIFF_MAP = {"Easy": 0, "Medium": 1, "Hard": 2}
TOPIC_MAP = {
    "Biology": 0, "Physics": 1, "Chemistry": 2,
    "Computer Science": 3, "Maths": 4, "History": 5, "General": 6
}
TOD_MAP = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}

FEATURE_COLS = [
    "days_since_last_review", "num_reviews", "past_accuracy",
    "avg_response_time", "hints_used", "diff_code", "topic_code", "tod_code"
]

_FORGETTING_CACHE = None

def load_training_data() -> pd.DataFrame:
    """
    Loads simulated seed logs from data/recall_logs_seed.csv.
    Ignores initial comment lines safely.
    """
    if not os.path.exists(SEED_DATA_PATH):
        raise FileNotFoundError(f"Recall seed data not found at: {SEED_DATA_PATH}")
    
    df = pd.read_csv(SEED_DATA_PATH, comment="#")
    return df

def preprocess_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Encodes categorical columns into numerical feature matrix X and target y."""
    X_list = []
    y_list = df["forgotten"].astype(int).values

    for _, row in df.iterrows():
        diff_code = DIFF_MAP.get(str(row["difficulty"]), 1)
        topic_code = TOPIC_MAP.get(str(row["topic"]), 6)
        tod_code = TOD_MAP.get(str(row.get("time_of_day", "afternoon")).lower(), 1)
        
        feats = [
            float(row["days_since_last_review"]),
            float(row["num_reviews"]),
            float(row["past_accuracy"]),
            float(row["avg_response_time"]),
            float(row.get("hints_used", 0)),
            float(diff_code),
            float(topic_code),
            float(tod_code)
        ]
        X_list.append(feats)

    return np.array(X_list), y_list

def evaluate_fixed_interval_baseline(X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """
    Baseline benchmark: Fixed-Interval rule (standard Leitner/fixed box approach).
    Heuristic: Predicts forgotten (1) if days elapsed exceeds simple threshold (e.g. 4.0 days).
    """
    days = X_test[:, 0]
    num_revs = X_test[:, 1]
    # Simple fixed rule: threshold = 2.5 * repetitions
    threshold = 2.5 * np.maximum(1.0, num_revs * 0.8)
    preds = (days > threshold).astype(int)
    # Continuous proxy for AUC: normalized days / threshold
    proxy_probs = 1.0 / (1.0 + np.exp(-(days - threshold)))

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    try:
        auc = roc_auc_score(y_test, proxy_probs)
    except Exception:
        auc = 0.5

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "auc": round(float(auc), 4)
    }

def train_forgetting_model(save_path: str = MODEL_PATH) -> Dict[str, Any]:
    """
    Trains Logistic Regression and Gradient Boosting models,
    compares them with the Fixed-Interval Baseline, and serializes the champion.
    """
    df = load_training_data()
    X, y = preprocess_features(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # 1. Baseline
    baseline_metrics = evaluate_fixed_interval_baseline(X_test, y_test)

    # 2. Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_probs = lr.predict_proba(X_test)[:, 1]
    lr_metrics = {
        "accuracy": round(float(accuracy_score(y_test, lr_preds)), 4),
        "precision": round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, lr_preds, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, lr_preds, zero_division=0)), 4),
        "auc": round(float(roc_auc_score(y_test, lr_probs)), 4)
    }

    # 3. Gradient Boosting Classifier
    gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
    gb.fit(X_train, y_train)
    gb_preds = gb.predict(X_test)
    gb_probs = gb.predict_proba(X_test)[:, 1]
    gb_metrics = {
        "accuracy": round(float(accuracy_score(y_test, gb_preds)), 4),
        "precision": round(float(precision_score(y_test, gb_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, gb_preds, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, gb_preds, zero_division=0)), 4),
        "auc": round(float(roc_auc_score(y_test, gb_probs)), 4)
    }

    # Select champion model based on ROC-AUC
    if gb_metrics["auc"] >= lr_metrics["auc"]:
        champion_name = "GradientBoosting"
        champion_model = gb
        champion_metrics = gb_metrics
    else:
        champion_name = "LogisticRegression"
        champion_model = lr
        champion_metrics = lr_metrics

    # Feature importances / coefficients
    feat_weights = {}
    if hasattr(champion_model, "feature_importances_"):
        for name, imp in zip(FEATURE_COLS, champion_model.feature_importances_):
            feat_weights[name] = round(float(imp), 4)
    elif hasattr(champion_model, "coef_"):
        for name, coef in zip(FEATURE_COLS, champion_model.coef_[0]):
            feat_weights[name] = round(float(coef), 4)

    bundle = {
        "model": champion_model,
        "champion_name": champion_name,
        "champion_metrics": champion_metrics,
        "lr_metrics": lr_metrics,
        "gb_metrics": gb_metrics,
        "baseline_metrics": baseline_metrics,
        "feature_weights": feat_weights,
        "trained_samples": len(df),
        "disclaimer": "Trained on simulated Ebbinghaus decay logs; indicative of relative forgetting probability."
    }

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(bundle, save_path)
    print(f"[Forgetting Model] Champion {champion_name} (AUC: {champion_metrics['auc']:.4f}) saved to: {save_path}")
    return bundle

def get_forgetting_bundle(save_path: str = MODEL_PATH) -> Dict[str, Any]:
    """Loads forgetting model bundle or trains on first invocation."""
    global _FORGETTING_CACHE
    if _FORGETTING_CACHE is not None:
        return _FORGETTING_CACHE

    if os.path.exists(save_path):
        try:
            _FORGETTING_CACHE = joblib.load(save_path)
            return _FORGETTING_CACHE
        except Exception:
            pass

    _FORGETTING_CACHE = train_forgetting_model(save_path=save_path)
    return _FORGETTING_CACHE

def predict_forgetting_risk(days_since_last_review: float,
                            num_reviews: int = 1,
                            past_accuracy: float = 0.8,
                            avg_response_time: float = 5.0,
                            hints_used: int = 0,
                            difficulty: str = "Medium",
                            topic: str = "General",
                            time_of_day: str = "afternoon") -> Dict[str, Any]:
    """
    Inference function for predicting current and future forgetting risk.
    Projects probabilities across 24h, 3d, and 7d horizons.
    """
    bundle = get_forgetting_bundle()
    model = bundle["model"]

    diff_code = DIFF_MAP.get(difficulty, 1)
    topic_code = TOPIC_MAP.get(topic, 6)
    tod_code = TOD_MAP.get(time_of_day.lower(), 1)

    # Base feature vector for current elapsed time
    base_feats = [
        float(days_since_last_review),
        float(num_reviews),
        float(past_accuracy),
        float(avg_response_time),
        float(hints_used),
        float(diff_code),
        float(topic_code),
        float(tod_code)
    ]

    prob_current = float(model.predict_proba([base_feats])[0][1])

    # Horizon projections (+1 day, +3 days, +7 days from now)
    feats_24h = list(base_feats); feats_24h[0] += 1.0
    feats_3d = list(base_feats);  feats_3d[0] += 3.0
    feats_7d = list(base_feats);  feats_7d[0] += 7.0

    prob_24h = float(model.predict_proba([feats_24h])[0][1])
    prob_3d = float(model.predict_proba([feats_3d])[0][1])
    prob_7d = float(model.predict_proba([feats_7d])[0][1])

    if prob_current >= 0.65:
        category = "High Risk"
    elif prob_current >= 0.35:
        category = "Medium Risk"
    else:
        category = "Low Risk"

    return {
        "current_forgetting_prob": round(prob_current, 3),
        "risk_category": category,
        "horizon_24h": round(prob_24h, 3),
        "horizon_3d": round(prob_3d, 3),
        "horizon_7d": round(prob_7d, 3)
    }

if __name__ == "__main__":
    train_forgetting_model()
