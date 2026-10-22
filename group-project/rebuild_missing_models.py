"""Offline recovery of missing artifacts from the group's original recipes.

Run once, before deployment. The serving apps never import or execute this file.
The original fraud classifier is recovered from Drive and is never retrained here.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
from urllib.request import urlopen

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "model"
OUTPUT_DIR.mkdir(exist_ok=True)
RANDOM_STATE = 42
EXPECTED = {
    "student_exam_score.csv": "ff859d9154c1059b5d80f579deffaa9c6fa2c2f863e6db9346a27bba0a9e6019",
    "bank_wealth_management.csv": "10bc0d435a39befe5911a068c4ed1e3c8c87fcf27ea252cd4e6f900fa2c6bfe6",
    "pharmacy_purchases.csv": "c599cd14fed6f2f06c16215161aa133a9d3acaf963fc9c686086bfdbe1fdc84b",
}


def read_verified(name, **kwargs):
    path = ROOT / "data" / name
    if not path.exists():
        source = ("https://raw.githubusercontent.com/course-files/RegressionAndClassification/main/data/"
                  if name == "student_exam_score.csv" else
                  "https://raw.githubusercontent.com/course-files/ClusteringandAssociationRuleMining/8733fd215f6bcd08168741220005458e38b8a090/data/")
        path.parent.mkdir(exist_ok=True)
        with urlopen(source + name, timeout=45) as response:
            content = response.read()
        assert hashlib.sha256(content).hexdigest() == EXPECTED[name], name
        path.write_bytes(content)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED[name], name
    return pd.read_csv(path, **kwargs)


def display(*args):
    pass


def recipe(name):
    path = ROOT / "source-recipes" / name
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), globals())


if __name__ == "__main__":
    # Exact selected-feature, split and tuning recipe from the group's notebook.
    df = read_verified("student_exam_score.csv")
    recipe("regression_recipe.py")
    assert abs(float(tuned_rmse) - 6.4941) < 0.001, "Regression differs from recorded notebook output"
    joblib.dump(tuned_model, OUTPUT_DIR / "exam_score_regressor.joblib")
    print("Recovered regression; held-out RMSE agrees with notebook.", flush=True)

    bank = read_verified("bank_wealth_management.csv").drop(columns="account_id")
    recipe("bank_recipe.py")
    sizes = sorted(np.bincount(bank_labels).tolist())
    assert sizes == [60, 299, 341], sizes
    profiles = bank.assign(cluster=bank_labels).groupby("cluster").mean(numeric_only=True)
    wealth = int(profiles["account_balance_kes"].idxmax())
    active = int(profiles.drop(index=wealth)["transactions_per_month"].idxmax())
    established = next(label for label in profiles.index if label not in [wealth, active])
    names = {wealth: "High-balance established accounts", active: "Active newer accounts",
             int(established): "Established lower-activity accounts"}
    joblib.dump({"pipeline": bank_model, "feature_columns": FEATURES, "segment_names": names,
                 "sklearn_version": importlib.metadata.version("scikit-learn")},
                OUTPUT_DIR / "bank_segmentation.joblib")
    print("Recovered bank pipeline; all three cluster sizes agree with notebook.", flush=True)

    pharmacy_raw = read_verified("pharmacy_purchases.csv", parse_dates=["transaction_date"])
    item_names = pharmacy_raw.drop_duplicates("item_id").set_index("item_id")["item_name"].to_dict()
    transactions = pharmacy_raw.groupby("receipt_id").agg(
        date=("transaction_date", "first"), items=("item_id", lambda s: sorted(set(s)))
    ).sort_values(["date", "receipt_id"])
    training = transactions.loc[transactions["date"] < pd.Timestamp("2025-06-01")]
    encoder = TransactionEncoder()
    encoded = pd.DataFrame(encoder.fit_transform(training["items"]), columns=encoder.columns_)
    frequent_itemsets = apriori(encoded, min_support=0.02, use_colnames=True)
    candidate_rules = association_rules(frequent_itemsets[["support", "itemsets"]],
                                       metric="confidence", min_threshold=0.0)
    strong_rules = candidate_rules.loc[candidate_rules.confidence.ge(.50) & candidate_rules.lift.ge(2.50)].copy()
    training_transactions = training  # Original cleanup cell uses this variable name.
    recipe("pharmacy_cleanup.py")
    assert [len(training), len(frequent_itemsets), len(candidate_rules), len(cleaned_rules)] == [3012, 30, 34, 11]
    records = [{"rule_id": row.rule_id, "antecedent": sorted(row.antecedents),
                "consequent": sorted(row.consequents), "confidence": float(row.confidence),
                "lift": float(row.lift), "support": float(row.support)}
               for row in cleaned_rules.itertuples()]
    lookup = {}
    for i, rule in enumerate(records):
        lookup.setdefault("|".join(rule["antecedent"]), []).append(i)
    bundle = {"cleaned_rules": records, "recommendation_lookup": lookup, "item_id_to_name": item_names}
    (OUTPUT_DIR / "pharmacy_recommender.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    manifest = {"recovery": "Three artifacts rebuilt offline from original notebook recipes; fraud pipeline recovered unchanged from Drive",
                "checks": {"regression_test_rmse": float(tuned_rmse), "bank_cluster_sizes": sizes,
                           "pharmacy_training_receipts": len(training), "pharmacy_cleaned_rules": len(records)},
                "versions": {name: importlib.metadata.version(name) for name in
                             ["numpy", "pandas", "scikit-learn", "joblib", "mlxtend"]},
                "model_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in OUTPUT_DIR.iterdir() if p.suffix in [".joblib", ".pkl", ".json"]}}
    (ROOT / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Recovered pharmacy rules; rule counts agree with notebook. Manifest saved.", flush=True)
