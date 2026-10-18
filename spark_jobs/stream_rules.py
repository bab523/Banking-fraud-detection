from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType

spark = (SparkSession.builder.appName("fraud_rules")
         .master("local[2]")
         .config("spark.driver.memory", "1g")
         .config("spark.sql.shuffle.partitions", "3")
         .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

fields = [StructField("Time", DoubleType())]
fields += [StructField(f"V{i}", DoubleType()) for i in range(1, 29)]
fields += [StructField("Amount", DoubleType()),
           StructField("Class", DoubleType()),
           StructField("txn_id", IntegerType())]
schema = StructType(fields)

raw = (spark.readStream.format("kafka")
       .option("kafka.bootstrap.servers", "localhost:9092,localhost:9094,localhost:9096")
       .option("subscribe", "txn_live")
       .option("startingOffsets", "earliest")
       .load())

parsed = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("d")).select("d.*")

scored = (parsed
    .withColumn("rule_high_amount", (F.col("Amount") > 1000).cast("int"))
    .withColumn("rule_v14", (F.col("V14") < -5).cast("int"))
    .withColumn("rule_v17", (F.col("V17") < -5).cast("int"))
    .withColumn("risk_score", F.col("rule_high_amount") + F.col("rule_v14") + F.col("rule_v17"))
    .withColumn("is_alert", (F.col("risk_score") >= 1).cast("int"))
    .select("txn_id", "Time", "Amount", "V14", "V17", "Class",
            "rule_high_amount", "rule_v14", "rule_v17", "risk_score", "is_alert"))

query = (scored.writeStream
         .format("parquet")
         .option("path", "data/output/scored")
         .option("checkpointLocation", "data/output/checkpoint")
         .outputMode("append")
         .trigger(processingTime="10 seconds")
         .start())
query.awaitTermination()
