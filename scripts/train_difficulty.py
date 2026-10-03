"""
Script to Train and Evaluate Difficulty Classification Models
Compares Logistic Regression, Random Forest, and Gradient Boosting.
Prints cross-validation scores, classification report, and feature importances.
Saves winning model to models/difficulty_model.joblib.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.difficulty_model import train_and_select_best_model, FEATURE_NAMES

def main():
    print("=" * 60)
    print("      LociLoom: Concept Difficulty Model Training       ")
    print("=" * 60)
    bundle = train_and_select_best_model()

    print("\n--- 5-Fold Cross Validation Results ---")
    for name, res in bundle["eval_results"].items():
        print(f"  {name:<20}: Mean Acc = {res['mean_acc']:.4f} (Std = {res['std_acc']:.4f})")

    print(f"\nWinning Model Selected: {bundle['model_name']} (Acc: {bundle['best_cv_score']:.4f})")

    print("\n--- Classification Report (Full Dataset) ---")
    rep = bundle["classification_report"]
    for label in ["Easy", "Medium", "Hard"]:
        if label in rep:
            p = rep[label]["precision"]
            r = rep[label]["recall"]
            f1 = rep[label]["f1-score"]
            supp = rep[label]["support"]
            print(f"  {label:<10}: Precision = {p:.3f}, Recall = {r:.3f}, F1 = {f1:.3f} (N={supp})")

    if bundle.get("feature_importances"):
        print("\n--- Feature Importances ---")
        sorted_feats = sorted(bundle["feature_importances"].items(), key=lambda x: x[1], reverse=True)
        for feat, imp in sorted_feats:
            bar = "#" * int(imp * 50)
            print(f"  {feat:<24}: {imp:.4f} {bar}")

    print("\nTraining completed successfully.")

if __name__ == "__main__":
    main()
