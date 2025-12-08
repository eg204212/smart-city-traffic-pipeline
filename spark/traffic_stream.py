from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("TrafficStream") \
    .getOrCreate()

schema = StructType([
    StructField("sensor_id", StringType()),
    StructField("timestamp", StringType()),
    StructField("vehicle_count", IntegerType()),
    StructField("avg_speed", IntegerType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "traffic-data") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

# Congestion Index = vehicle_count / avg_speed
result = json_df.withColumn(
    "congestion_index",
    col("vehicle_count") / col("avg_speed")
)

# Write alerts → speed < 10
critical = json_df.filter(col("avg_speed") < 10)

critical.writeStream \
    .format("console") \
    .start()

# Window aggregation (5-minute)
windowed = result \
    .withColumn("timestamp", col("timestamp").cast("timestamp")) \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("sensor_id")
    ) \
    .avg("congestion_index", "vehicle_count")

windowed.writeStream \
    .format("console") \
    .outputMode("update") \
    .start() \
    .awaitTermination()
