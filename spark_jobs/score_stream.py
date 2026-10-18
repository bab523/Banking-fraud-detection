import json, joblib
import pandas as pd
from datetime import datetime
from kafka import KafkaConsumer

model = joblib.load("models/model.joblib")
thr = json.load(open("dashboard_data/metrics.json"))["threshold"]

consumer = KafkaConsumer("txn_live", bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest", consumer_timeout_ms=5000,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")))
df = pd.DataFrame([m.value for m in consumer]).drop_duplicates("txn_id").reset_index(drop=True)

df["fraud_probability"] = model.predict_proba(df[list(model.feature_names_in_)])[:, 1].round(4)
df["prediction"] = (df["fraud_probability"] >= thr).astype(int)
df["decision"] = df["prediction"].map({1: "FRAUD", 0: "LEGITIMATE"})

rules = pd.DataFrame({
    "r_amount": df["Amount"] > 1000, "r_v14": df["V14"] < -3, "r_v12": df["V12"] < -3,
    "r_v10": df["V10"] < -3, "r_v4": df["V4"] > 3, "r_v11": df["V11"] > 2.5}).astype(int)
df["rule_score"] = rules.sum(axis=1)
df["rule_alert"] = (df["rule_score"] >= 2).astype(int)

out = pd.DataFrame({
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "transaction_id": df["txn_id"].apply(lambda x: f"TXN-{x:05d}"),
    "amount": df["Amount"].round(2), "fraud_probability": df["fraud_probability"],
    "threshold": thr, "prediction": df["prediction"], "decision": df["decision"],
    "rule_score": df["rule_score"], "rule_alert": df["rule_alert"],
    "actual_class": df["Class"].astype(int)})
out.to_parquet("dashboard_data/predictions.parquet")
print(out.shape)
print(pd.crosstab(out["actual_class"], out["prediction"], rownames=["actual"], colnames=["ML"]))
print(pd.crosstab(out["actual_class"], out["rule_alert"], rownames=["actual"], colnames=["rules"]))
