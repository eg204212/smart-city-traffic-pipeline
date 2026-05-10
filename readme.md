# 🚦 Smart City Traffic Management System

**Big Data Engineering Project**

Monitor real-time traffic from 4 junctions in Colombo, detect congestion, and generate daily reports for traffic police deployment.

--------------------------------------------

## 📌 What This Project Does

1. **Simulates Traffic Sensors** - 4 junctions sending data every 2 seconds
2. **Real-Time Monitoring** - Detects critical traffic when speed < 10 km/h
3. **Batch Analysis** - Nightly job finds peak traffic hours
4. **Reports** - Generates charts showing Traffic Volume vs Time

---------------------------------------------

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

-----------------------------------------------------

## 🛠️ Technologies Used

- **Apache Kafka** - Message streaming
- **Python** - Data processing & producers
- **PostgreSQL** - Data storage
- **Apache Airflow** - Job scheduling
- **Docker** - Containerization
- **Matplotlib** - Visualizations
3. **Airflow**: Robust DAG-based orchestration for scheduled batch analytics
4. **PostgreSQL**: ACID compliance for reliable historical data storage with SQL query support

----------------------------------------------------

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

-----------------------------------------------------------
