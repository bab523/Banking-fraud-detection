# Real-Time Banking Fraud Detection Platform

Data Engineering capstone project (Group 1).

## Architecture
Producer (Kaggle creditcard.csv) -> Kafka (3 brokers, KRaft, topic txn_live: 3 partitions, replication 3) -> Rule engine -> Parquet -> Streamlit dashboard

## Results
- 1000 transactions (150 fraud, 850 normal)
- 144 alerts, 138 frauds caught, detection rate 92%

## Run
    docker compose up -d
    python producer/producer.py
    python spark_jobs/stream_rules_lite.py
    streamlit run producer/dashboard.py

## Fault tolerance
One Kafka broker stopped (docker stop kafka2): cluster and producer kept working; ISR recovered after restart.

## Limitations
Laptop has 4.8 GB RAM, so HBase, Hive, Airflow and Spark Structured Streaming were replaced by lightweight alternatives (Kafka consumer, Parquet, Streamlit).
