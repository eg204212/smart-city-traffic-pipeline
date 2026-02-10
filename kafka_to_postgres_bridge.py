"""
Simple bridge to move data from Kafka to PostgreSQL without Spark
This bypasses the Spark streaming requirement when dependencies can't be downloaded
"""
import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

print("🔄 Starting Kafka to PostgreSQL Bridge...")

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="trafficdb",
    user="airflow",
    password="airflow"
)
cursor = conn.cursor()

# Kafka consumer
consumer = KafkaConsumer(
    'traffic-data',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',  
    group_id='postgres-bridge-group'
)

print("✅ Connected to Kafka and PostgreSQL")
print("📡 Listening for traffic data...")
print("Press Ctrl+C to stop\n")

message_count = 0
critical_count = 0

try:
    for message in consumer:
        data = message.value
        
        # Insert into traffic_data table
        insert_query = """
        INSERT INTO traffic_data (sensor_id, event_time, vehicle_count, avg_speed, congestion_index, hour_of_day)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        event_time = datetime.fromisoformat(data['timestamp'])
        hour_of_day = event_time.hour
        
        cursor.execute(insert_query, (
            data['sensor_id'],
            event_time,
            data['vehicle_count'],
            data['avg_speed'],
            data['congestion_index'],
            hour_of_day
        ))
        
        message_count += 1
        
        # If critical traffic (speed < 10), also insert into alerts table
        if data['avg_speed'] < 10:
            alert_query = """
            INSERT INTO critical_traffic_alerts (sensor_id, event_time, vehicle_count, avg_speed, congestion_index)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(alert_query, (
                data['sensor_id'],
                event_time,
                data['vehicle_count'],
                data['avg_speed'],
                data['congestion_index']
            ))
            critical_count += 1
            print(f"🚨 CRITICAL ALERT: {data['sensor_id']} - Speed: {data['avg_speed']} km/h")
        
        # Commit every 10 messages
        if message_count % 10 == 0:
            conn.commit()
            print(f"✅ Processed {message_count} messages ({critical_count} critical alerts)")
        
except KeyboardInterrupt:
    print(f"\n\n⏹️ Stopping bridge...")
    print(f"📊 Total messages processed: {message_count}")
    print(f"🚨 Total critical alerts: {critical_count}")
    conn.commit()
    cursor.close()
    conn.close()
    consumer.close()
    print("✅ Bridge stopped successfully")
