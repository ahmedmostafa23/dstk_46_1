"""
Configurable ML Pipeline
=========================
Reads pipeline_config.yaml and runs:
  1. Load data  (csv / json / excel / parquet)
  2. Select features & target
  3. Preprocess  (scale numericals, encode categoricals)
  4. Train model
  5. Evaluate
"""

import yaml
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# ── Registry maps: config string → class ────────────────────

LOADERS = {
    "csv":     pd.read_csv,
    "json":    pd.read_json,
    "excel":   pd.read_excel,
    "parquet": pd.read_parquet,
}

def _get_scaler(name: str, args: dict):
    from sklearn.preprocessing import (
        StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
    )
    scalers = {
        "standard": StandardScaler,
        "minmax":   MinMaxScaler,
        "robust":   RobustScaler,
        "maxabs":   MaxAbsScaler,
    }
    if name not in scalers:
        raise ValueError(f"Unknown scaler '{name}'. Choose from: {list(scalers)}")
    return scalers[name](**args)

def _get_encoder(name: str, args: dict):
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, TargetEncoder
    encoders = {
        "onehot":  OneHotEncoder,
        "ordinal": OrdinalEncoder,
        "target":  TargetEncoder,
    }
    if name not in encoders:
        raise ValueError(f"Unknown encoder '{name}'. Choose from: {list(encoders)}")
    return encoders[name](**args)

def _get_model(name: str, args: dict):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    models = {
        "logistic_regression": LogisticRegression,
        "random_forest":       RandomForestClassifier,
        "svm":                 SVC,
        "knn":                 KNeighborsClassifier,
        "decision_tree":       DecisionTreeClassifier,
    }
    if name not in models:
        raise ValueError(f"Unknown model '{name}'. Choose from: {list(models)}")
    return models[name](**args)

METRICS = {
    "accuracy": lambda y, yp, yprob: accuracy_score(y, yp),
    "f1":       lambda y, yp, yprob: f1_score(y, yp, average="weighted"),
    "roc_auc":  lambda y, yp, yprob: roc_auc_score(y, yprob[:, 1])
                                  if yprob is not None else None,
}

# ── Pipeline steps ──────────────────────────────────────────

def load_data(cfg: dict) -> pd.DataFrame:
    loader_name = cfg["loader"]
    if loader_name not in LOADERS:
        raise ValueError(f"Unknown loader '{loader_name}'. Choose from: {list(LOADERS)}")
    loader_fn = LOADERS[loader_name]
    args = cfg.get("args", {}) or {}
    print(f"[1/5] Loading data from '{cfg['path']}' with {loader_name}({args})")
    return loader_fn(cfg["path"], **args)


def select_features(df: pd.DataFrame, cfg: dict):
    target_col = cfg["target"]
    num_cols = cfg.get("numerical", []) or []
    cat_cols = cfg.get("categorical", []) or []
    feature_cols = num_cols + cat_cols

    print(f"[2/5] Target: '{target_col}' | "
          f"Numerical: {num_cols} | Categorical: {cat_cols}")

    X = df[feature_cols]
    y = df[target_col]
    return X, y, num_cols, cat_cols


def build_preprocessor(num_cols, cat_cols, preproc_cfg):
    scaler_cfg  = preproc_cfg.get("scaler", {})
    encoder_cfg = preproc_cfg.get("encoder", {})

    scaler  = _get_scaler(scaler_cfg.get("type", "standard"),
                          scaler_cfg.get("args", {}) or {})
    encoder = _get_encoder(encoder_cfg.get("type", "onehot"),
                           encoder_cfg.get("args", {}) or {})

    print(f"[3/5] Scaler: {scaler.__class__.__name__} | "
          f"Encoder: {encoder.__class__.__name__}")

    transformers = []
    if num_cols:
        transformers.append(("num", scaler, num_cols))
    if cat_cols:
        transformers.append(("cat", encoder, cat_cols))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_pipeline(preprocessor, model_cfg):
    model = _get_model(model_cfg.get("type", "logistic_regression"),
                       model_cfg.get("args", {}) or {})
    print(f"[4/5] Model:  {model.__class__.__name__}")
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def evaluate(pipeline, X_test, y_test, metric_names):
    y_pred = pipeline.predict(X_test)

    # attempt probability predictions for roc_auc
    y_prob = None
    if hasattr(pipeline, "predict_proba"):
        try:
            y_prob = pipeline.predict_proba(X_test)
        except Exception:
            pass

    print("[5/5] Evaluation:")
    results = {}
    for name in metric_names:
        fn = METRICS.get(name)
        if fn is None:
            print(f"  ⚠  Unknown metric '{name}', skipping.")
            continue
        val = fn(y_test, y_pred, y_prob)
        if val is not None:
            results[name] = val
            print(f"  • {name:12s} = {val:.4f}")
        else:
            print(f"  • {name:12s} = N/A")
    return results


# ── Main ────────────────────────────────────────────────────

def run(config_path: str = "pipeline_config.yaml"):
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 1. Load
    df = load_data(cfg["data"])

    # 2. Select
    X, y, num_cols, cat_cols = select_features(df, cfg["features"])

    # 3. Preprocess + 4. Model
    preprocessor = build_preprocessor(num_cols, cat_cols, cfg["preprocessing"])
    pipeline = build_pipeline(preprocessor, cfg["model"])

    # Train / test split
    eval_cfg = cfg.get("evaluation", {}) or {}
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=eval_cfg.get("test_size", 0.2),
        random_state=eval_cfg.get("random_state", 42),
    )

    pipeline.fit(X_train, y_train)

    # 5. Evaluate
    metrics = eval_cfg.get("metrics", ["accuracy"])
    evaluate(pipeline, X_test, y_test, metrics)

    return pipeline


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "pipeline_config.yaml"
    run(path)