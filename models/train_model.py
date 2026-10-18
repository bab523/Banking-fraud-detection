import json, joblib
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (precision_recall_curve, roc_auc_score, average_precision_score,
                             confusion_matrix, precision_score, recall_score, f1_score)

df = pd.read_csv("data/creditcard.csv")
X, y = df.drop(columns="Class"), df["Class"]

# 60% train, 20% validation, 20% test
X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.4, stratify=y, random_state=42)
X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=42)

# train mein normal rows kam karo (RAM bachane ke liye)
tr = pd.concat([X_tr[y_tr == 1], X_tr[y_tr == 0].sample(30000, random_state=42)])
y_b = y_tr.loc[tr.index]

model = RandomForestClassifier(n_estimators=150, max_depth=10, min_samples_leaf=2,
                               class_weight="balanced", n_jobs=2, random_state=42)
model.fit(tr, y_b)

# threshold validation set se chuno (test set ko haath nahi lagaya)
p_val = model.predict_proba(X_val)[:, 1]
prec, rec, thr = precision_recall_curve(y_val, p_val)
f1 = 2 * prec * rec / (prec + rec + 1e-9)
threshold = float(thr[np.argmax(f1[:-1])])

# final test (asli ratio 0.17%)
p_te = model.predict_proba(X_te)[:, 1]
pred = (p_te >= threshold).astype(int)
tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)

metrics = {
    "threshold": round(threshold, 3),
    "test_rows": int(len(y_te)), "test_frauds": int(y_te.sum()),
    "precision": round(precision_score(y_te, pred), 4),
    "recall": round(recall_score(y_te, pred), 4),
    "f1": round(f1_score(y_te, pred), 4),
    "roc_auc": round(roc_auc_score(y_te, p_te), 4),
    "pr_auc": round(average_precision_score(y_te, p_te), 4),
    "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    "top_features": {k: round(float(v), 4) for k, v in imp.items()},
}
json.dump(metrics, open("dashboard_data/metrics.json", "w"), indent=2)
joblib.dump(model, "models/model.joblib")

# demo sample: test set se 100 fraud + 900 normal
te = X_te.copy(); te["Class"] = y_te
demo = pd.concat([te[te.Class == 1].head(100), te[te.Class == 0].head(900)]).sample(frac=1, random_state=1)
demo.to_csv("data/test_sample.csv", index=False)
print(json.dumps(metrics, indent=2))
