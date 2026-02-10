"""
Smart City Traffic Data Producer
Simulates traffic sensor data from 4 junctions in Colombo
Generates realistic traffic patterns with occasional congestion
"""
import json
import time
import random
import os
from kafka import KafkaProducer
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Kafka Producer
# Get Kafka host from environment variable or use localhost
kafka_host = os.getenv('KAFKA_HOST', 'kafka:9092')
producer = KafkaProducer(
    bootstrap_servers=[kafka_host],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    retry_backoff_ms=1000
)

# Junction configurations with realistic traffic patterns
JUNCTIONS = {
    "J1_Galle_Road": {"base_count": 180, "congestion_prob": 0.15},
    "J2_Duplication_Road": {"base_count": 150, "congestion_prob": 0.20},
    "J3_Baseline_Road": {"base_count": 120, "congestion_prob": 0.12},
    "J4_Marine_Drive": {"base_count": 100, "congestion_prob": 0.10}
}

def get_hour_multiplier():
    """Returns traffic multiplier based on hour of day (rush hours have more traffic)"""
    hour = datetime.now().hour
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Morning and evening rush hours
        return 1.8
    elif 10 <= hour <= 16:  # Mid-day
        return 1.2
    elif 22 <= hour or hour <= 5:  # Late night
        return 0.4
    return 1.0

def generate_traffic_data(junction_id, config):
    """Generate realistic traffic data for a junction"""
    hour_multiplier = get_hour_multiplier()
    
    # Vehicle count with realistic variation
    base = config["base_count"]
    vehicle_count = int(base * hour_multiplier + random.randint(-30, 30))
    vehicle_count = max(10, vehicle_count)  # Minimum 10 vehicles
    
    # Speed logic: occasionally create congestion (speed < 10 km/h)
    if random.random() < config["congestion_prob"]:
        # Critical congestion
        avg_speed = random.randint(3, 9)
        logger.warning(f"🚨 CONGESTION ALERT at {junction_id}: Speed={avg_speed} km/h")
    elif random.random() < 0.3:
        # Moderate traffic
        avg_speed = random.randint(15, 25)
    else:
        # Normal traffic
        avg_speed = random.randint(30, 60)
    
    return {
        "sensor_id": junction_id,
        "timestamp": datetime.now().isoformat(),
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
        "congestion_index": round(vehicle_count / avg_speed, 2)
    }

def main():
    """Main producer loop"""
    logger.info("🚀 Starting Smart City Traffic Producer...")
    logger.info(f"📡 Monitoring {len(JUNCTIONS)} junctions")
    
    message_count = 0
    
    try:
        while True:
            # Send data from all junctions
            for junction_id, config in JUNCTIONS.items():
                data = generate_traffic_data(junction_id, config)
                
                producer.send("traffic-data", data)
                message_count += 1
                
                # Clean logging
                status = "🔴 CRITICAL" if data["avg_speed"] < 10 else "🟢 NORMAL"
                logger.info(
                    f"{status} | {junction_id} | "
                    f"Vehicles: {data['vehicle_count']:3d} | "
                    f"Speed: {data['avg_speed']:2d} km/h | "
                    f"Index: {data['congestion_index']:.2f}"
                )
            
            time.sleep(2)  # Send data every 2 seconds
            
    except KeyboardInterrupt:
        logger.info(f"\n✅ Producer stopped. Total messages sent: {message_count}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()

