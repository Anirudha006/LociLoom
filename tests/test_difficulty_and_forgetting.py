"""
Tests for ML Difficulty and Forgetting Curve models.
"""

import pytest
from core.difficulty_model import extract_features, predict_difficulty
from core.forgetting_model import predict_forgetting_risk


def test_extract_difficulty_features():
    features = extract_features(
        concept="Deoxyribonucleic acid",
        sentence="Deoxyribonucleic acid carries genetic instructions.",
        topic="Biology"
    )
    assert len(features) == 8
    # Word count
    assert features[0] == 2.0
    # Char length
    assert features[1] == len("Deoxyribonucleic acid")
    # Syllable count should be >= 5
    assert features[2] >= 5


def test_predict_difficulty():
    # Simple word vs complex multi-syllabic jargon
    label_s, conf_s, feats_s = predict_difficulty("Tree", "A tree has green leaves.", "Biology")
    label_c, conf_c, feats_c = predict_difficulty(
        "Phosphofructokinase phosphorylation",
        "Phosphofructokinase phosphorylation regulates glycolysis allosterically.",
        "Biology"
    )
    assert label_s in ["Easy", "Medium", "Hard"]
    assert label_c in ["Easy", "Medium", "Hard"]
    assert 0.0 <= conf_s <= 1.0
    assert 0.0 <= conf_c <= 1.0
    assert "char_length" in feats_s
    assert "syllable_count" in feats_c


def test_predict_forgetting_risk():
    # Freshly reviewed easy item: lower risk
    risk_fresh = predict_forgetting_risk(
        days_since_last_review=0.5,
        num_reviews=4,
        past_accuracy=1.0,
        avg_response_time=3.0,
        hints_used=0,
        difficulty="Easy",
        topic="Biology"
    )
    assert "current_forgetting_prob" in risk_fresh
    assert "risk_category" in risk_fresh
    assert "horizon_24h" in risk_fresh
    assert "horizon_3d" in risk_fresh
    assert "horizon_7d" in risk_fresh
    assert risk_fresh["risk_category"] in ["Low Risk", "Medium Risk", "High Risk"]

    # Neglected hard item: higher risk
    risk_neglected = predict_forgetting_risk(
        days_since_last_review=25.0,
        num_reviews=1,
        past_accuracy=0.3,
        avg_response_time=9.0,
        hints_used=2,
        difficulty="Hard",
        topic="Biology"
    )
    assert risk_neglected["current_forgetting_prob"] >= risk_fresh["current_forgetting_prob"]
    # Horizon risk increases over time
    assert risk_fresh["horizon_7d"] >= risk_fresh["horizon_24h"]
