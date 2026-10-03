"""
LociLoom Experiment Statistical Evaluation Suite
Calculates comparative empirical metrics for Experiment Mode:
- Condition A (Standard Rote/Linear Notes) vs Condition B (LociLoom Memory Palace)
Calculates:
- Means, standard deviations, and median scores
- Paired t-test (parametric) or Wilcoxon signed-rank test (non-parametric) via scipy
- Cohen's d effect size formulation
- Honest, plain-language scientific interpretation highlighting statistical power and sample size limits
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats

def calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
    """Calculates Cohen's d effect size for paired or independent samples."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0

    mean1, mean2 = float(np.mean(group1)), float(np.mean(group2))
    var1, var2 = float(np.var(group1, ddof=1)), float(np.var(group2, ddof=1))

    # Pooled standard deviation
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return round((mean2 - mean1) / pooled_sd, 3)

def analyze_experiment_results(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes student evaluation records comparing:
    Condition A: Standard Note Reading
    Condition B: LociLoom Memory Palace Method
    """
    if not records:
        return {
            "has_data": False,
            "message": "No experiment participant trials recorded yet."
        }

    cond_a_scores = []
    cond_b_scores = []
    cond_a_times = []
    cond_b_times = []
    cond_a_satis = []
    cond_b_satis = []

    for r in records:
        cond = str(r.get("condition", "")).strip().upper()
        score = float(r.get("immediate_score", 0.0))
        study_time = float(r.get("study_time", 0.0))
        satis = float(r.get("satisfaction", 3.0))

        if "CONDITION A" in cond or "LINEAR" in cond or cond == "A":
            cond_a_scores.append(score)
            cond_a_times.append(study_time)
            cond_a_satis.append(satis)
        else:
            cond_b_scores.append(score)
            cond_b_times.append(study_time)
            cond_b_satis.append(satis)

    n_a, n_b = len(cond_a_scores), len(cond_b_scores)
    if n_a == 0 or n_b == 0:
        return {
            "has_data": False,
            "n_a": n_a,
            "n_b": n_b,
            "message": "Need participant data for both Condition A and Condition B to compute comparative statistics."
        }

    mean_a = float(np.mean(cond_a_scores))
    std_a = float(np.std(cond_a_scores, ddof=1)) if n_a > 1 else 0.0
    mean_b = float(np.mean(cond_b_scores))
    std_b = float(np.std(cond_b_scores, ddof=1)) if n_b > 1 else 0.0

    # Effect size (Cohen's d)
    d = calculate_cohens_d(cond_a_scores, cond_b_scores)

    # Statistical Significance Test
    # If equal sample size, compute paired t-test & Wilcoxon; otherwise independent t-test
    p_value = 1.0
    test_name = "Independent Two-Sample t-Test"

    if n_a == n_b and n_a >= 3:
        try:
            # Paired t-test
            t_stat, p_val = stats.ttest_rel(cond_b_scores, cond_a_scores)
            p_value = float(p_val)
            test_name = "Paired Student's t-Test"
        except Exception:
            try:
                # Wilcoxon signed-rank fallback
                w_stat, p_val = stats.wilcoxon(cond_b_scores, cond_a_scores)
                p_value = float(p_val)
                test_name = "Wilcoxon Signed-Rank Test (Non-Parametric)"
            except Exception:
                p_value = 1.0
    elif n_a >= 2 and n_b >= 2:
        try:
            t_stat, p_val = stats.ttest_ind(cond_b_scores, cond_a_scores, equal_var=False)
            p_value = float(p_val)
            test_name = "Welch's Independent t-Test"
        except Exception:
            p_value = 1.0

    # Interpretation text
    total_n = n_a + n_b
    if total_n < 10:
        power_warning = f"⚠️ Small sample size (N={total_n}). Results are exploratory and should not be generalized without larger trial replication."
    else:
        power_warning = f"Sample size (N={total_n}) provides initial comparative evidence across conditions."

    if p_value < 0.05:
        sig_text = f"Statistically significant difference observed (p = {p_value:.4f} < 0.05)."
    else:
        sig_text = f"Difference is not statistically significant at alpha = 0.05 (p = {p_value:.4f})."

    # Magnitude interpretation of Cohen's d
    abs_d = abs(d)
    if abs_d >= 0.8:
        effect_str = "Large effect size"
    elif abs_d >= 0.5:
        effect_str = "Medium effect size"
    elif abs_d >= 0.2:
        effect_str = "Small effect size"
    else:
        effect_str = "Negligible effect size"

    summary = (
        f"Condition B (LociLoom) achieved an average recall score of {mean_b:.1f}% (SD={std_b:.1f}%), "
        f"compared to {mean_a:.1f}% (SD={std_a:.1f}%) for Condition A (Standard Notes). "
        f"{sig_text} Effect size was Cohen's d = {d:.2f} ({effect_str}). {power_warning}"
    )

    return {
        "has_data": True,
        "n_a": n_a,
        "n_b": n_b,
        "mean_score_a": round(mean_a, 2),
        "std_score_a": round(std_a, 2),
        "mean_score_b": round(mean_b, 2),
        "std_score_b": round(std_b, 2),
        "mean_time_a": round(float(np.mean(cond_a_times)), 1),
        "mean_time_b": round(float(np.mean(cond_b_times)), 1),
        "mean_satis_a": round(float(np.mean(cond_a_satis)), 2),
        "mean_satis_b": round(float(np.mean(cond_b_satis)), 2),
        "cohens_d": d,
        "effect_magnitude": effect_str,
        "p_value": round(p_value, 4),
        "test_name": test_name,
        "is_significant": (p_value < 0.05),
        "interpretation": summary,
        "power_warning": power_warning
    }
