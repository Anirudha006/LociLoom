"""
LociLoom Topic Classifier
Classifies student notes into one of 7 academic subjects:
- Biology, Physics, Chemistry, Computer Science, Maths, History, General
Trained on data/concepts_seed.csv using TF-IDF + Logistic Regression with calibrated probabilities.
Serializes to models/topic_classifier.joblib and auto-trains if missing.
"""
import os
import joblib
import pandas as pd
from typing import Tuple, Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "topic_classifier.joblib")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "concepts_seed.csv")

_MODEL_CACHE = None

def train_topic_model(data_path: str = DATA_PATH, model_save_path: str = MODEL_PATH) -> Pipeline:
    """Trains TF-IDF + Logistic Regression topic classifier and saves to joblib."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Concepts seed data not found at: {data_path}")

    df = pd.read_csv(data_path)
    # Combine concept name and context sentence for rich lexical features
    texts = (df["concept"].fillna("") + " " + df["context_sentence"].fillna("")).tolist()
    labels = df["topic"].tolist()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42))
    ])

    # 5-fold cross validation score
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, texts, labels, cv=cv, scoring="accuracy")
    print(f"[Topic Classifier] 5-Fold CV Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")

    # Fit on all available seed data
    pipeline.fit(texts, labels)

    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(pipeline, model_save_path)
    print(f"[Topic Classifier] Model saved to: {model_save_path}")
    return pipeline

def get_topic_model(model_path: str = MODEL_PATH) -> Pipeline:
    """Loads the cached model or trains a new one if not present on disk."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    if os.path.exists(model_path):
        try:
            _MODEL_CACHE = joblib.load(model_path)
            return _MODEL_CACHE
        except Exception:
            pass

    # Model missing or corrupted: auto-train
    _MODEL_CACHE = train_topic_model(model_save_path=model_path)
    return _MODEL_CACHE

DOMAIN_KEYWORDS = {
    "Computer Science": [
        "machine learning", "neural network", "algorithm", "deep learning", "artificial intelligence",
        "database", "programming", "python", "software", "tcp/ip", "packet", "ethernet", "router",
        "supervised learning", "unsupervised learning", "reinforcement learning", "data structure",
        "hardware", "operating system", "code", "compiler", "sql", "server", "cybersecurity",
        "computer", "model training", "feature extraction"
    ],
    "Biology": [
        "photosynthesis", "chlorophyll", "chloroplast", "mitochondria", "cell", "dna", "rna",
        "organism", "mitosis", "meiosis", "enzyme", "ecosystem", "bacteria", "species", "gene",
        "respiration", "transpiration", "xylem", "phloem", "stomata", "biology", "plants"
    ],
    "Physics": [
        "newton", "inertia", "gravity", "force", "velocity", "acceleration", "thermodynamics",
        "kinetic", "momentum", "electromagnetism", "quantum", "relativity", "friction", "optics",
        "wavelength", "photon", "thermodynamic"
    ],
    "Chemistry": [
        "molecule", "atom", "reaction", "acid", "base", "periodic table", "covalent", "ionic",
        "electron", "valency", "organic chemistry", "polymer", "catalyst", "solution", "solvent"
    ],
    "Maths": [
        "calculus", "derivative", "integral", "matrix", "algebra", "probability", "geometry",
        "theorem", "equation", "vector", "logarithm", "trigonometry", "polynomial"
    ],
    "History": [
        "war", "dynasty", "revolution", "empire", "treaty", "century", "monarch", "civilization",
        "reign", "battle", "independence", "colony", "constitution", "renaissance"
    ]
}

def classify_topic(text: str) -> Tuple[str, float]:
    """
    Predicts the academic subject for an input text or set of concepts.
    Combines trained TF-IDF Logistic Regression with domain keyword signals.
    Returns: (predicted_topic, confidence_probability)
    """
    if not text or not text.strip():
        return ("General", 0.5)

    lower_text = text.lower()

    # Check for direct keyword matches
    keyword_scores = {topic: 0 for topic in DOMAIN_KEYWORDS}
    for topic, kws in DOMAIN_KEYWORDS.items():
        for kw in kws:
            if kw in lower_text:
                # Multi-word matches get higher weight
                keyword_scores[topic] += 2 if " " in kw else 1

    top_keyword_topic = max(keyword_scores, key=keyword_scores.get)
    if keyword_scores[top_keyword_topic] >= 2:
        return (top_keyword_topic, 0.95)

    model = get_topic_model()
    probs = model.predict_proba([text])[0]
    classes = model.classes_
    best_idx = probs.argmax()

    # If keyword signal exists, give strong weight
    if keyword_scores[top_keyword_topic] >= 1:
        return (top_keyword_topic, max(0.85, float(probs[best_idx])))

    return (str(classes[best_idx]), round(float(probs[best_idx]), 3))

def get_topic_probabilities(text: str) -> Dict[str, float]:
    """Returns probability distribution across all 7 topic domains."""
    if not text or not text.strip():
        return {"General": 1.0}
    model = get_topic_model()
    probs = model.predict_proba([text])[0]
    return {cls: round(float(p), 3) for cls, p in zip(model.classes_, probs)}

if __name__ == "__main__":
    train_topic_model()
