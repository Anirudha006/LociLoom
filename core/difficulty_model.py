"""
LociLoom Concept Difficulty Predictor
Extracts linguistic, cognitive, and structural features from concepts:
- Syllable count & readability estimates
- Word length & character count
- Abstractness / Concreteness ratings (lexicon + morphological fallback)
- Lexical rarity score
- Presence of digits, Greek symbols, or scientific notation
- Topic domain context
Trained using Gradient Boosting / Random Forest / Logistic Regression on data/concepts_seed.csv.
"""
import os
import re
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "difficulty_model.joblib")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "concepts_seed.csv")

# Built-in Concreteness / Abstractness Lexicon (Scale 1.0 = Highly Abstract, 5.0 = Concrete Object)
# Based on psycholinguistic norms (Brysbaert et al.)
CONCRETENESS_LEXICON = {
    # Highly concrete (4.5 - 5.0)
    "apple": 5.0, "bottle": 5.0, "balloon": 4.9, "sponge": 4.9, "tree": 4.9,
    "truck": 4.9, "router": 4.8, "sugar": 4.8, "scissors": 5.0, "cube": 4.7,
    "battery": 4.8, "scroll": 4.7, "bridge": 4.8, "lamp": 4.9, "water": 4.7,
    "coin": 4.9, "nail": 4.9, "rock": 4.9, "car": 4.8, "bell": 4.8,
    "hat": 4.9, "book": 4.8, "desk": 4.9, "sofa": 4.9, "door": 4.9,
    # Moderately concrete (3.0 - 4.4)
    "plant": 4.3, "sunlight": 4.1, "cell": 3.8, "steam": 4.0, "ice": 4.5,
    "wire": 4.6, "smoke": 4.2, "crystal": 4.4, "milk": 4.7, "gas": 3.6,
    "sound": 3.5, "wave": 3.4, "current": 3.2, "charge": 3.0, "circuit": 3.7,
    # Abstract concepts (1.0 - 2.9)
    "theory": 1.4, "entropy": 1.3, "relativity": 1.5, "quantum": 1.6, "infinity": 1.2,
    "probability": 1.7, "democracy": 2.0, "justice": 1.5, "feudalism": 2.1,
    "mutation": 2.4, "homeostasis": 1.9, "concurrency": 1.8, "recursion": 2.0,
    "polymorphism": 1.7, "inheritance": 2.4, "deadlock": 2.2, "encryption": 2.3,
    "osmosis": 2.5, "calculus": 1.9, "derivative": 2.1, "integral": 2.2,
    "eigenvalue": 1.5, "asymptote": 1.8, "stoichiometry": 1.9, "enthalpy": 1.6,
    "neuroplasticity": 2.0, "metacognition": 1.3, "interference": 2.2, "chunking": 2.5
}

TOPIC_MAP = {
    "Biology": 0, "Physics": 1, "Chemistry": 2,
    "Computer Science": 3, "Maths": 4, "History": 5, "General": 6
}

FEATURE_NAMES = [
    "word_count", "char_length", "syllable_count", "abstractness_score",
    "word_rarity", "has_digits_or_symbols", "sentence_length",
    "topic_code"
]

_DIFFICULTY_CACHE = None

def estimate_syllables(word: str) -> int:
    """Estimates syllables in an English word via vowel phoneme clusters."""
    w = word.lower().strip()
    if len(w) <= 3:
        return 1
    # Remove trailing non-vocalic 'e'
    w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
    w = re.sub(r'^y', '', w)
    matches = re.findall(r'[aeiouy]{1,2}', w)
    return max(1, len(matches))

def calculate_abstractness(phrase: str) -> float:
    """
    Returns an abstractness score between 1.0 (very abstract) and 5.0 (concrete).
    Uses lexicon lookup with documented morphological suffix fallback.
    """
    words = re.findall(r'\b[a-zA-Z]+\b', phrase.lower())
    if not words:
        return 2.5
    
    scores = []
    for w in words:
        if w in CONCRETENESS_LEXICON:
            scores.append(CONCRETENESS_LEXICON[w])
        else:
            # Suffix-based morphological fallback heuristics
            if w.endswith(("tion", "sion", "ity", "ism", "ness", "ment", "ence", "ance")):
                scores.append(1.8) # High abstraction noun suffixes
            elif w.endswith(("logy", "ics", "phy", "try", "sis")):
                scores.append(2.1) # Academic field / scientific process suffixes
            elif w.endswith(("able", "ible", "ous", "al", "ic", "ive")):
                scores.append(2.6) # Descriptive adjective suffixes
            elif len(w) > 9:
                scores.append(2.4)
            else:
                scores.append(3.2) # Default neutral concrete fallback

    return float(np.mean(scores))

def calculate_rarity(phrase: str) -> float:
    """Estimates lexical rarity based on length and rare phonemes (z, x, q, ph, th)."""
    clean = phrase.lower()
    rare_chars = sum(clean.count(ch) for ch in ["z", "x", "q", "j", "k", "v"])
    length_factor = len(clean) / 15.0
    return min(1.0, (rare_chars * 0.15) + (length_factor * 0.4))

def extract_features(concept: str, sentence: str = "", topic: str = "General") -> List[float]:
    """Extracts the 8 numerical features for the difficulty model."""
    words = concept.split()
    word_count = len(words)
    char_length = len(concept)
    
    syllables = sum(estimate_syllables(w) for w in words)
    abstractness = calculate_abstractness(concept)
    rarity = calculate_rarity(concept)
    
    has_digits = 1.0 if re.search(r'[0-9\^_\-+/=\(\)]', concept) else 0.0
    sent_len = len(sentence.split()) if sentence else word_count * 3
    
    topic_code = float(TOPIC_MAP.get(topic, 6))

    return [
        float(word_count),
        float(char_length),
        float(syllables),
        float(abstractness),
        float(rarity),
        float(has_digits),
        float(sent_len),
        float(topic_code)
    ]

def train_and_select_best_model(data_path: str = DATA_PATH, save_path: str = MODEL_PATH):
    """
    Compares Logistic Regression, Random Forest, and Gradient Boosting via 5-fold CV.
    Saves the best performing model to joblib and returns performance metrics.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Concepts seed data missing at: {data_path}")

    df = pd.read_csv(data_path)
    X = []
    y = df["difficulty"].tolist()

    for _, row in df.iterrows():
        feat = extract_features(str(row["concept"]), str(row.get("context_sentence", "")), str(row.get("topic", "General")))
        X.append(feat)

    X = np.array(X)
    y = np.array(y)

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    best_name = None
    best_score = -1.0
    best_model = None
    eval_results = {}

    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
        mean_acc = scores.mean()
        std_acc = scores.std()
        eval_results[name] = {"mean_acc": mean_acc, "std_acc": std_acc}
        print(f"[{name}] 5-Fold CV Accuracy: {mean_acc:.4f} (+/- {std_acc:.4f})")
        if mean_acc > best_score:
            best_score = mean_acc
            best_name = name
            best_model = model

    # Fit best model on full dataset
    best_model.fit(X, y)
    y_pred = best_model.predict(X)
    report = classification_report(y, y_pred, output_dict=True)

    # Feature importances if available
    feat_importances = {}
    if hasattr(best_model, "feature_importances_"):
        for name, imp in zip(FEATURE_NAMES, best_model.feature_importances_):
            feat_importances[name] = round(float(imp), 4)

    payload = {
        "model": best_model,
        "model_name": best_name,
        "best_cv_score": best_score,
        "eval_results": eval_results,
        "feature_importances": feat_importances,
        "classification_report": report
    }

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(payload, save_path)
    print(f"[Difficulty Model] Saved best model ({best_name}, Acc: {best_score:.4f}) to: {save_path}")
    return payload

def get_difficulty_bundle(save_path: str = MODEL_PATH) -> Dict[str, Any]:
    """Loads difficulty model bundle from disk or trains on first run."""
    global _DIFFICULTY_CACHE
    if _DIFFICULTY_CACHE is not None:
        return _DIFFICULTY_CACHE

    if os.path.exists(save_path):
        try:
            _DIFFICULTY_CACHE = joblib.load(save_path)
            return _DIFFICULTY_CACHE
        except Exception:
            pass

    _DIFFICULTY_CACHE = train_and_select_best_model(save_path=save_path)
    return _DIFFICULTY_CACHE

def predict_difficulty(concept: str, sentence: str = "", topic: str = "General") -> Tuple[str, float, Dict[str, Any]]:
    """
    Predicts concept difficulty: Easy, Medium, or Hard.
    Returns: (predicted_difficulty, confidence, feature_dict)
    """
    bundle = get_difficulty_bundle()
    model = bundle["model"]
    
    feats = extract_features(concept, sentence, topic)
    probs = model.predict_proba([feats])[0]
    classes = model.classes_
    best_idx = probs.argmax()
    
    diff_label = classes[best_idx]
    confidence = float(probs[best_idx])
    
    feature_dict = dict(zip(FEATURE_NAMES, feats))
    return (str(diff_label), round(confidence, 3), feature_dict)

if __name__ == "__main__":
    train_and_select_best_model()
