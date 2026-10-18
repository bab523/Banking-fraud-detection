# Real-Time Banking Fraud Detection Platform

Data Engineering capstone project (Group 1).

## Architecture
Producer (Kaggle creditcard.csv) -> Kafka (3 brokers, KRaft, txn_live: 3 partitions, RF 3) -> ML scoring (Random Forest) + rule engine -> Parquet -> Streamlit dashboard

## Model results (held-out test set, 56,962 rows, 99 frauds)
Precision 0.917, Recall 0.778, F1 0.842, ROC-AUC 0.978, 7 false alarms, 22 missed frauds.

## Run
    docker compose up -d
    python models/train_model.py
    python producer/producer.py
    python spark_jobs/score_stream.py
    streamlit run producer/dashboard.py

## Fault tolerance
kafka2 stopped: ISR shrank, producer kept working; ISR restored after restart. See docs/.

## Limitations
4.8 GB RAM laptop: Spark Streaming, HBase, Hive and Airflow replaced by lightweight tools. Scoring runs as a micro-batch.
