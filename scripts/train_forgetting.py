"""
Script to Train and Evaluate Forgetting Prediction Models
Evaluates Logistic Regression and Gradient Boosting against a Fixed-Interval Baseline.
Reports Accuracy, Precision, Recall, F1, and ROC-AUC metrics honestly.
Saves champion model to models/forgetting_model.joblib.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.forgetting_model import train_forgetting_model, FEATURE_COLS

def main():
    print("=" * 65)
    print("      LociLoom: Adaptive Forgetting Predictor Training       ")
    print("=" * 65)
    bundle = train_forgetting_model()

    print(f"\nTraining Dataset: {bundle['trained_samples']} samples (Bootstrapped simulated decay logs)")
    print(f"Disclaimer: {bundle['disclaimer']}")

    print("\n" + "=" * 65)
    print(f"{'Model Architecture':<24} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<6} | {'F1':<6} | {'ROC-AUC':<7}")
    print("-" * 65)

    base = bundle["baseline_metrics"]
    print(f"{'Fixed-Interval Baseline':<24} | {base['accuracy']:<8.4f} | {base['precision']:<9.4f} | {base['recall']:<6.4f} | {base['f1']:<6.4f} | {base['auc']:<7.4f}")

    lr = bundle["lr_metrics"]
    print(f"{'Logistic Regression':<24} | {lr['accuracy']:<8.4f} | {lr['precision']:<9.4f} | {lr['recall']:<6.4f} | {lr['f1']:<6.4f} | {lr['auc']:<7.4f}")

    gb = bundle["gb_metrics"]
    print(f"{'Gradient Boosting (ML)':<24} | {gb['accuracy']:<8.4f} | {gb['precision']:<9.4f} | {gb['recall']:<6.4f} | {gb['f1']:<6.4f} | {gb['auc']:<7.4f}")
    print("=" * 65)

    print(f"\nWinning Model Selected: {bundle['champion_name']} (ROC-AUC: {bundle['champion_metrics']['auc']:.4f})")

    if bundle.get("feature_weights"):
        print("\n--- Key Factor Influence on Forgetting ---")
        sorted_weights = sorted(bundle["feature_weights"].items(), key=lambda x: abs(x[1]), reverse=True)
        for feat, val in sorted_weights:
            bar = "#" * int(abs(val) * 40)
            print(f"  {feat:<25}: {val:.4f} {bar}")

    print("\nModel training and comparative evaluation complete.")

if __name__ == "__main__":
    main()
