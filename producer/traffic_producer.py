import json, time, random
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

junctions = ["J1", "J2", "J3", "J4"]

while True:
    data = {
        "sensor_id": random.choice(junctions),
        "timestamp": datetime.now().isoformat(),
        "vehicle_count": random.randint(50, 250),
        "avg_speed": random.choice([5, 8, 12, 20, 40, 60])  # occasionally < 10
    }

    producer.send("traffic-data", data)
    print("Sent:", data)
    time.sleep(1)

