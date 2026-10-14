CREATE TABLE IF NOT EXISTS customers (
  customer_id INT PRIMARY KEY,
  name VARCHAR(100),
  city VARCHAR(50),
  risk_tier VARCHAR(10) DEFAULT 'LOW'
);

CREATE TABLE IF NOT EXISTS transactions (
  txn_id INT PRIMARY KEY,
  customer_id INT,
  amount DECIMAL(12,2),
  txn_time INT,
  is_fraud TINYINT
);
