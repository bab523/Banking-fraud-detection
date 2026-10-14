import json, time
import pandas as pd
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092", "localhost:9094", "localhost:9096"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
)

df = pd.read_csv("data/creditcard.csv", nrows=1000)

for i, row in df.iterrows():
    msg = row.to_dict()
    msg["txn_id"] = int(i)
    producer.send("txn_live", msg)
    if i % 100 == 0:
        print("sent", i)
    time.sleep(0.05)

producer.flush()
print("done")
