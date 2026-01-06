# 🚦 Smart City Traffic & Congestion Management System

## Big Data Engineering Mini Project - Scenario 1

A complete **Lambda Architecture** implementation for real-time traffic monitoring and batch analytics using Apache Kafka, Spark Streaming, PostgreSQL, and Airflow.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Pipeline](#-running-the-pipeline)
- [Project Structure](#-project-structure)
- [Data Flow](#-data-flow)
- [Monitoring & Alerts](#-monitoring--alerts)
- [Reports & Analytics](#-reports--analytics)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

The city of Colombo modernizes its traffic management by deploying IoT sensors at major intersections. This system:

- **Ingests** real-time traffic data from 4 junctions (sensors broadcast every 2 seconds)
- **Processes** streams with 5-minute tumbling windows to calculate congestion indices
- **Alerts** when average speed drops below 10 km/h (critical congestion)
- **Orchestrates** nightly batch jobs to identify peak traffic hours
- **Recommends** which junctions need physical police intervention

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Traffic Sensors│  (4 Junctions - Mock Producers)
│  J1, J2, J3, J4 │
└────────┬────────┘
         │ JSON Stream
         ▼
┌─────────────────┐
│  Apache Kafka   │  Topic: traffic-data
│  (Message Broker)│
└────────┬────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  Spark Streaming│              │  Kafka Consumer │
│  (Stream Layer) │              │  (Optional)     │
└────────┬────────┘              └─────────────────┘
         │
         ├── 5-min Windows ──→ Congestion Index
         ├── Filter (speed<10)─→ Critical Alerts
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  Tables: traffic_data, 
│   (Storage)     │          critical_alerts,
└────────┬────────┘          daily_reports
         │
         ▼
┌─────────────────┐
│ Apache Airflow  │  DAG: Nightly @ 11:59 PM
│ (Batch Layer)   │  - Peak Hour Analysis
└────────┬────────┘  - Intervention Recommendations
         │            - Report Generation
         ▼
┌─────────────────┐
│  Reports Folder │  PNG Charts + CSV Exports
└─────────────────┘
```

**Architecture Type**: **Lambda Architecture**
- **Speed Layer**: Kafka + Spark Streaming (real-time alerts)
- **Batch Layer**: Airflow + PostgreSQL (historical analysis)
- **Serving Layer**: PostgreSQL views + Generated reports

---

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Data Ingestion** | Apache Kafka | Latest | Message broker for traffic events |
| **Stream Processing** | Apache Spark (PySpark) | 3.5.0 | Real-time stream processing |
| **Batch Orchestration** | Apache Airflow | 2.7.0 | Workflow scheduling & DAG execution |
| **Database** | PostgreSQL | 14 | Persistent storage for traffic data |
| **Containerization** | Docker Compose | 3.8 | Multi-container deployment |
| **Visualization** | Matplotlib, Seaborn | - | Data visualization |

### Justification:
1. **Kafka**: High-throughput, low-latency event streaming platform ideal for IoT sensor data
2. **Spark Streaming**: Scalable stream processing with windowing support for time-series aggregation
3. **Airflow**: Robust DAG-based orchestration for scheduled batch analytics
4. **PostgreSQL**: ACID compliance for reliable historical data storage with SQL query support

---

## ✨ Features

### Real-Time Processing (Stream Layer)
- ✅ Ingests traffic data every 2 seconds from 4 junctions
- ✅ Calculates congestion index: `vehicle_count / avg_speed`
- ✅ 5-minute tumbling window aggregations
- ✅ Critical traffic alerts when `avg_speed < 10 km/h`
- ✅ Stores all events in PostgreSQL for batch processing

### Batch Processing (Orchestration Layer)
- ✅ Scheduled nightly at 11:59 PM
- ✅ Identifies peak traffic hour per junction
- ✅ Calculates daily traffic statistics
- ✅ Generates intervention recommendations
- ✅ Creates visualizations (heatmaps, time-series plots)

### Event Time vs Processing Time Handling
- **Event Time**: Timestamp from sensor (when traffic event occurred)
- **Processing Time**: When Spark processes the record
- **Watermarking**: 10-minute watermark for handling late-arriving data
- **Windows**: 5-minute tumbling windows based on event time

---

## 📦 Prerequisites

- Docker Desktop (20.10+)
- Docker Compose (3.8+)
- 8 GB RAM minimum (16 GB recommended)
- 10 GB free disk space

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd smart-city-traffic-project
```

### 2. Project Structure
```
smart-city-traffic-project/
├── docker-compose.yml           # Multi-container orchestration
├── database/
│   └── init.sql                 # PostgreSQL schema initialization
├── producer/
│   ├── traffic_producer.py      # Kafka producer (sensor simulator)
│   ├── Dockerfile
│   └── requirements.txt
├── spark/
│   └── traffic_stream.py        # Spark Streaming application
├── airflow/
│   ├── dags/
│   │   └── daily_traffic_report.py  # Airflow DAG
│   ├── logs/
│   └── requirements.txt
├── reports/
│   └── generate_report.py       # Manual report generator
└── readme.md
```

### 3. Start the Infrastructure
```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Services will be available at:**
- Kafka: `localhost:9092`
- Spark Master UI: `http://localhost:8080`
- Airflow Web UI: `http://localhost:8085` (admin/admin)
- PostgreSQL: `localhost:5432`

### 4. Initialize Database
```bash
# Execute initialization script (runs automatically on first start)
docker exec -i postgres psql -U airflow -d trafficdb < database/init.sql
```

### 5. Verify Data Flow
```bash
# Check producer logs
docker logs -f traffic-producer

# Check Spark streaming logs
docker logs -f traffic-stream-processor

# Check Airflow scheduler
docker logs -f airflow-scheduler
```

---

## ▶️ Running the Pipeline

### Step 1: Start Data Generation
The producer starts automatically with `docker-compose up`. Monitor it:
```bash
docker logs -f traffic-producer
```

**Expected Output:**
```
🟢 NORMAL | J1_Galle_Road | Vehicles: 180 | Speed: 45 km/h | Index: 4.00
🔴 CRITICAL | J2_Duplication_Road | Vehicles: 220 | Speed: 8 km/h | Index: 27.50
```

### Step 2: Monitor Stream Processing
```bash
docker logs -f traffic-stream-processor
```

**Spark writes to:**
1. PostgreSQL `traffic_data` table (all events)
2. PostgreSQL `critical_traffic_alerts` table (speed < 10)
3. Console output (5-min window aggregations)

### Step 3: Verify Database Storage
```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U airflow -d trafficdb

# Query recent data
SELECT sensor_id, event_time, vehicle_count, avg_speed, congestion_index 
FROM traffic_data 
ORDER BY event_time DESC 
LIMIT 10;

# Check critical alerts
SELECT * FROM critical_traffic_alerts ORDER BY event_time DESC LIMIT 5;
```

### Step 4: Trigger Airflow DAG
```bash
# Access Airflow UI: http://localhost:8085
# Login: admin / admin
# Enable DAG: smart_city_daily_traffic_report

# Manual trigger (or wait for 11:59 PM scheduled run)
docker exec airflow-scheduler airflow dags trigger smart_city_daily_traffic_report
```

### Step 5: View Generated Reports
```bash
# Reports are saved in reports/ folder
ls -lh reports/

# View latest report
docker exec airflow-webserver ls -lh /opt/airflow/reports/
```

---

## 📊 Data Flow

### Producer → Kafka
```json
{
  "sensor_id": "J1_Galle_Road",
  "timestamp": "2026-01-06T14:30:15.123456",
  "vehicle_count": 180,
  "avg_speed": 8,
  "congestion_index": 22.5
}
```

### Kafka → Spark → PostgreSQL
**Schema: traffic_data**
| Column | Type | Description |
|--------|------|-------------|
| sensor_id | VARCHAR | Junction identifier |
| event_time | TIMESTAMP | When event occurred |
| vehicle_count | INTEGER | Number of vehicles |
| avg_speed | INTEGER | Average speed (km/h) |
| congestion_index | DOUBLE | vehicle_count / avg_speed |
| traffic_status | BOOLEAN | True if speed < 10 |
| hour_of_day | INTEGER | Hour (0-23) |

### Airflow → Reports
**Output Files:**
- `daily_traffic_analysis_YYYYMMDD.png` - Visualization dashboard
- `daily_traffic_report_YYYYMMDD.csv` - Intervention recommendations

---

## 🚨 Monitoring & Alerts

### Critical Traffic Detection
When `avg_speed < 10 km/h`:
1. Event written to `critical_traffic_alerts` table
2. Logged in Spark console: `🚨 CRITICAL ALERT`
3. Included in nightly report for intervention planning

### Health Checks
```bash
# Check all containers
docker-compose ps

# Check Kafka topics
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Check Spark jobs
curl http://localhost:8080  # Spark Master UI

# Check Airflow DAGs
curl http://localhost:8085/health  # Airflow health endpoint
```

---

## 📈 Reports & Analytics

### Daily Report Contents
1. **Traffic Volume vs. Time** - Line chart showing hourly trends
2. **Congestion Heatmap** - Junction × Hour heatmap
3. **Average Speed by Junction** - Bar chart with critical thresholds
4. **Intervention Recommendations** - Table with priority levels

### Sample Report Query
```sql
-- Get today's peak hours
SELECT sensor_id, peak_hour, peak_hour_vehicle_count, requires_intervention
FROM daily_traffic_reports
WHERE report_date = CURRENT_DATE
ORDER BY requires_intervention DESC, peak_hour_vehicle_count DESC;
```

### Manual Report Generation
```bash
# Run from reports/ directory (requires Python environment)
python reports/generate_report.py
```
---

## 🔧 Troubleshooting

### Issue: Kafka connection refused
```bash
# Restart Kafka and Zookeeper
docker-compose restart zookeeper kafka

# Wait 30 seconds, then restart dependent services
docker-compose restart traffic-producer traffic-stream-processor
```

### Issue: Spark job not receiving data
```bash
# Check Kafka topic has data
docker exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic traffic-data \
  --from-beginning \
  --max-messages 5
```

### Issue: Airflow DAG not visible
```bash
# Restart scheduler
docker-compose restart airflow-scheduler

# Check logs
docker logs airflow-scheduler
```

### Issue: PostgreSQL connection error
```bash
# Verify database is ready
docker exec postgres pg_isready -U airflow

# Check tables exist
docker exec postgres psql -U airflow -d trafficdb -c "\dt"
```

---

## 📚 Ethics & Privacy Considerations

### Privacy Implications
1. **Anonymization**: Sensor data does NOT include vehicle identification (license plates, RFID)
2. **Aggregation**: Data analyzed at junction level, not individual vehicle tracking
3. **Retention**: Historical data retained for 90 days only (configurable)
4. **Purpose Limitation**: Data used ONLY for traffic management, not surveillance

### Data Governance Recommendations
- Implement access controls (RBAC) for PostgreSQL
- Encrypt data at rest and in transit (TLS for Kafka)
- Regular audits of data access logs
- Compliance with local data protection regulations
- Transparent communication with citizens about data collection

---

## 🎓 Learning Outcomes Demonstrated

✅ **LO1**: Designed Lambda Architecture with speed & batch layers  
✅ **LO2**: Implemented Kafka producers with realistic traffic patterns  
✅ **LO3**: Developed Spark Streaming with windowing & watermarking  
✅ **LO4**: Orchestrated batch jobs using Airflow DAGs  
✅ **LO5**: Handled Event Time vs Processing Time with watermarks  
✅ **LO6**: Analyzed ethics of smart city surveillance systems  

---

## 👥 Team Members
- [Your Names Here]

## 📅 Submission Date
January 2026

## 📄 License
Academic Project - Not for Commercial Use

---

**🎯 Project Status**: Production-Ready ✅

For questions or issues, contact: [your-email@example.com]
