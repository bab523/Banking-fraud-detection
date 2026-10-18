import json
import pandas as pd
from kafka import KafkaConsumer

consumer = KafkaConsumer("txn_live",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    consumer_timeout_ms=5000,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")))

df = pd.DataFrame([m.value for m in consumer]).drop_duplicates("txn_id")
df["rule_high_amount"] = (df["Amount"] > 1000).astype(int)
df["rule_v14"] = (df["V14"] < -3).astype(int)
df["rule_v12"] = (df["V12"] < -3).astype(int)
df["rule_v10"] = (df["V10"] < -3).astype(int)
df["rule_v4"] = (df["V4"] > 3).astype(int)
df["rule_v11"] = (df["V11"] > 2.5).astype(int)
rules = ["rule_high_amount","rule_v14","rule_v12","rule_v10","rule_v4","rule_v11"]
df["risk_score"] = df[rules].sum(axis=1)
df["is_alert"] = (df["risk_score"] >= 2).astype(int)
cols = ["txn_id","Time","Amount","V14","V12","V10","V4","V11","Class"] + rules + ["risk_score","is_alert"]
df[cols].to_parquet("data/output/scored.parquet")
print(df.shape)
print(pd.crosstab(df["Class"], df["is_alert"]))
