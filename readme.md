# 🚦 Smart City Traffic Management System

**Big Data Engineering Project**

Monitor real-time traffic from 4 junctions in Colombo, detect congestion, and generate daily reports for traffic police deployment.

---

## 📌 What This Project Does

1. **Simulates Traffic Sensors** - 4 junctions sending data every 2 seconds
2. **Real-Time Monitoring** - Detects critical traffic when speed < 10 km/h
3. **Batch Analysis** - Nightly job finds peak traffic hours
4. **Reports** - Generates charts showing Traffic Volume vs Time

---

## 🏗️ System Architecture

```
Traffic Sensors (4 Junctions)
        ↓
   Apache Kafka (Message Queue)
        ↓
   Stream Processor (Real-time)
        ↓
   PostgreSQL Database
        ↓
   Apache Airflow (Nightly Reports)
```

**Lambda Architecture:**
- **Speed Layer**: Kafka → Stream Processing → Alerts
- **Batch Layer**: Airflow → Analysis → Reports

---

## 🛠️ Technologies Used

- **Apache Kafka** - Message streaming
- **Python** - Data processing & producers
- **PostgreSQL** - Data storage
- **Apache Airflow** - Job scheduling
- **Docker** - Containerization
- **Matplotlib** - Visualizations
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
---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Python 3.9+ installed
- 8GB RAM recommended

### Step 1: Start All Services
```bash
# Start everything with Docker
docker-compose up -d

# Check all containers are running
docker ps
```

### Step 2: Verify Data is Flowing
```bash
# Check producer is sending data
docker logs traffic-producer --tail 20

# Check database has records
docker exec postgres psql -U airflow -d trafficdb -c "SELECT COUNT(*) FROM traffic_data;"

# View latest traffic data
docker exec postgres psql -U airflow -d trafficdb -c "SELECT * FROM traffic_data ORDER BY event_time DESC LIMIT 5;"
```

### Step 3: Access Airflow Dashboard
```
Open browser: http://localhost:8085
Username: admin
Password: admin
```

### Step 4: Generate Reports
```bash
# Install dependencies
pip install pandas matplotlib seaborn psycopg2-binary

# Run report generator
python reports/generate_report.py
```

---

## 📂 Project Structure

```
smart-city-traffic-project/
├── producer/              # Traffic data generator
│   └── traffic_producer.py
├── spark/                 # Stream processing
│   └── traffic_stream.py
├── airflow/dags/          # Batch analysis jobs
│   └── daily_traffic_report.py
├── database/              # Database schema
│   └── init.sql
├── reports/               # Generated reports
│   └── generate_report.py
├── kafka_to_postgres_bridge.py  # Alternative stream processor
├── docker-compose.yml     # Infrastructure setup
└── README.md
```

---

## 📊 What Gets Generated

### Real-Time Alerts
- 🔴 Critical traffic when speed < 10 km/h
- Stored in `critical_traffic_alerts` table

### Daily Reports
- Peak traffic hour for each junction
- Traffic police intervention recommendations
- Traffic Volume vs Time charts (PNG)
- Summary statistics (CSV)

---

## 🔍 Sample Data

**Traffic Data:**
```
Junction: J1_Galle_Road
Time: 2026-02-10 08:15:30
Vehicles: 280
Speed: 8 km/h
Congestion Index: 35.0 🔴 CRITICAL
```

**Database Tables:**
1. `traffic_data` - All traffic events
2. `critical_traffic_alerts` - Speed < 10 km/h events
3. `daily_traffic_reports` - Airflow analysis results

---

## 🛠️ Useful Commands

### View Real-Time Kafka Messages
```bash
docker exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic traffic-data \
  --max-messages 10
```

### Query Traffic Statistics
```bash
# Records per junction
docker exec postgres psql -U airflow -d trafficdb -c \
  "SELECT sensor_id, COUNT(*) FROM traffic_data GROUP BY sensor_id;"

# Critical alerts count
docker exec postgres psql -U airflow -d trafficdb -c \
  "SELECT COUNT(*) FROM critical_traffic_alerts;"
```

### Stop All Services
```bash
docker-compose down
```

---

## 📈 Project Features

✅ **4 Junction Sensors** - J1_Galle_Road, J2_Duplication_Road, J3_Baseline_Road, J4_Marine_Drive  
✅ **Real-Time Processing** - 2-second data intervals  
✅ **Congestion Detection** - Speed < 10 km/h triggers alerts  
✅ **5-Minute Windows** - Tumbling window aggregations  
✅ **Batch Analytics** - Nightly peak hour analysis  
✅ **Automated Reports** - Traffic Volume vs Time visualizations  
✅ **Lambda Architecture** - Speed + Batch layers  
✅ **Docker Deployment** - One-command setup  

---

## 🎓 Project Requirements Met

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Data Source | Python producer (4 junctions) | ✅ |
| Kafka Ingestion | `traffic-data` topic | ✅ |
| Stream Processing | Real-time processor | ✅ |
| Windowing | 5-minute tumbling windows | ✅ |
| Critical Alerts | Speed < 10 km/h detection | ✅ |
| Airflow Orchestration | Nightly DAG | ✅ |
| Peak Hour Analysis | Daily aggregation | ✅ |
| Police Recommendations | Intervention logic | ✅ |
| Visualization | Traffic Volume vs Time | ✅ |

---

## 📝 Additional Files

- `PROJECT_REPORT.md` - 1500+ word technical report
- `ARCHITECTURE_DETAILED.md` - Complete architecture diagram
- `VERIFICATION_REPORT.md` - Requirements verification
- `SCREENSHOT_GUIDE.md` - Submission screenshot guide

---
**🎉 Project Complete! All scenario requirements satisfied.**
