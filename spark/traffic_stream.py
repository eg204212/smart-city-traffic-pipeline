"""
Smart City Traffic Stream Processing with Apache Spark
- Ingests real-time traffic data from Kafka
- Calculates congestion index with 5-minute tumbling windows
- Generates critical traffic alerts when avg_speed < 10 km/h
- Stores all data in PostgreSQL for batch processing
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, window, avg, sum as spark_sum, 
    count, max as spark_max, min as spark_min, 
    current_timestamp, to_timestamp, date_format, hour
)
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    IntegerType, DoubleType, TimestampType
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Spark Session with PostgreSQL support
spark = SparkSession.builder \
    .appName("SmartCityTrafficStream") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "org.postgresql:postgresql:42.6.0") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema for incoming traffic data
traffic_schema = StructType([
    StructField("sensor_id", StringType(), False),
    StructField("timestamp", StringType(), False),
    StructField("vehicle_count", IntegerType(), False),
    StructField("avg_speed", IntegerType(), False),
    StructField("congestion_index", DoubleType(), True)
])

# PostgreSQL configuration
postgres_config = {
    "url": "jdbc:postgresql://postgres:5432/trafficdb",
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}

logger.info("🚀 Starting Smart City Traffic Stream Processor...")

# Read stream from Kafka
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9093") \
    .option("subscribe", "traffic-data") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parse JSON data
parsed_df = df_stream.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), traffic_schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_time", to_timestamp(col("timestamp"))) \
    .withColumn("processing_time", current_timestamp())

# Calculate derived metrics
enriched_df = parsed_df.withColumn(
    "traffic_status",
    col("avg_speed") < 10
).withColumn(
    "hour_of_day",
    hour(col("event_time"))
)

# ====================
# STREAM 1: Store ALL data to PostgreSQL (for Airflow batch processing)
# ====================
def write_to_postgres(batch_df, batch_id):
    """Write each micro-batch to PostgreSQL"""
    if batch_df.isEmpty():
        return
    
    try:
        batch_df.select(
            "sensor_id",
            "event_time",
            "vehicle_count",
            "avg_speed",
            "congestion_index",
            "traffic_status",
            "hour_of_day",
            "processing_time"
        ).write \
            .format("jdbc") \
            .option("url", postgres_config["url"]) \
            .option("dbtable", "traffic_data") \
            .option("user", postgres_config["user"]) \
            .option("password", postgres_config["password"]) \
            .option("driver", postgres_config["driver"]) \
            .mode("append") \
            .save()
        
        logger.info(f"✅ Batch {batch_id}: {batch_df.count()} records written to PostgreSQL")
    except Exception as e:
        logger.error(f"❌ Error writing batch {batch_id}: {e}")

postgres_query = enriched_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint/postgres") \
    .start()

# ====================
# STREAM 2: Critical Traffic Alerts (avg_speed < 10 km/h)
# ====================
critical_traffic = enriched_df.filter(col("avg_speed") < 10)

def write_critical_alerts(batch_df, batch_id):
    """Write critical traffic alerts to separate table and Kafka topic"""
    if batch_df.isEmpty():
        return
    
    try:
        # Write to PostgreSQL alerts table
        batch_df.select(
            "sensor_id",
            "event_time",
            "vehicle_count",
            "avg_speed",
            "congestion_index"
        ).write \
            .format("jdbc") \
            .option("url", postgres_config["url"]) \
            .option("dbtable", "critical_traffic_alerts") \
            .option("user", postgres_config["user"]) \
            .option("password", postgres_config["password"]) \
            .option("driver", postgres_config["driver"]) \
            .mode("append") \
            .save()
        
        alert_count = batch_df.count()
        logger.warning(f"🚨 CRITICAL ALERT Batch {batch_id}: {alert_count} congestion events detected!")
        
        # Log individual alerts
        batch_df.select("sensor_id", "avg_speed", "vehicle_count").show(truncate=False)
        
    except Exception as e:
        logger.error(f"❌ Error writing alerts batch {batch_id}: {e}")

alerts_query = critical_traffic.writeStream \
    .foreachBatch(write_critical_alerts) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint/alerts") \
    .start()

# ====================
# STREAM 3: 5-Minute Tumbling Window Aggregations
# ====================
windowed_aggregation = enriched_df \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("sensor_id")
    ) \
    .agg(
        avg("congestion_index").alias("avg_congestion_index"),
        avg("vehicle_count").alias("avg_vehicle_count"),
        avg("avg_speed").alias("avg_speed"),
        spark_max("vehicle_count").alias("max_vehicle_count"),
        spark_min("avg_speed").alias("min_speed"),
        count("*").alias("record_count")
    )

# Console output for monitoring
console_query = windowed_aggregation.writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", "false") \
    .option("checkpointLocation", "/tmp/checkpoint/console") \
    .start()

logger.info("📊 All streaming queries started successfully!")
logger.info("📡 Monitoring traffic from 4 junctions...")
logger.info("⏰ Using 5-minute tumbling windows for aggregation")

# Wait for all streams to terminate
try:
    spark.streams.awaitAnyTermination()
except KeyboardInterrupt:
    logger.info("🛑 Stopping stream processing...")
    spark.stop()
