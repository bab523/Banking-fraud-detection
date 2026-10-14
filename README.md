# Real-Time Banking Fraud Detection Platform

Data Engineering capstone project.

## Stack
- Kafka (3 brokers, KRaft), topic `txn_live` (3 partitions, replication 3)
- MySQL 8
- Python producer (Kaggle creditcard.csv replay)

## Run
    docker compose up -d
    python producer/producer.py
