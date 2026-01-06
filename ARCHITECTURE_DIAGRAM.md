# Architecture Diagram Guide

## Creating the Architecture Diagram

For your project report, create a visual architecture diagram using tools like:
- **draw.io** (https://app.diagrams.net/) - Free, web-based
- **Lucidchart** (https://www.lucidchart.com/) - Professional diagrams
- **Microsoft Visio** - If available
- **PowerPoint** - Simple flowcharts

## Recommended Diagram Elements

### 1. Data Sources Layer
```
┌─────────────────────────────────────────┐
│        Traffic Sensors (Producers)       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│  │  J1  │ │  J2  │ │  J3  │ │  J4  │   │
│  │Galle │ │Dupli-│ │Base- │ │Marine│   │
│  │ Road │ │cation│ │line  │ │Drive │   │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘   │
└─────┼────────┼────────┼────────┼────────┘
      │        │        │        │
      └────────┴────────┴────────┘
               │ JSON Stream
               ▼
```

### 2. Ingestion Layer
```
┌─────────────────────────────────────────┐
│           Apache Kafka                   │
│  ┌────────────────────────────────────┐ │
│  │  Topic: traffic-data               │ │
│  │  Partitions: 4                     │ │
│  │  Retention: 24 hours               │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 3. Processing Layer - Lambda Architecture

**Speed Layer (Real-Time):**
```
┌─────────────────────────────────────────┐
│      Apache Spark Streaming              │
│  ┌────────────────────────────────────┐ │
│  │  Structured Streaming              │ │
│  │  - 5-minute tumbling windows       │ │
│  │  - Watermarking (10 min)           │ │
│  │  - Congestion index calculation    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Critical Alert Filter             │ │
│  │  IF avg_speed < 10 km/h            │ │
│  │  THEN write to alerts table        │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Batch Layer (Historical Analysis):**
```
┌─────────────────────────────────────────┐
│         Apache Airflow                   │
│  ┌────────────────────────────────────┐ │
│  │  DAG: daily_traffic_report         │ │
│  │  Schedule: @daily (11:59 PM)       │ │
│  │                                    │ │
│  │  Tasks:                            │ │
│  │  1. Extract yesterday's data       │ │
│  │  2. Analyze peak hours             │ │
│  │  3. Generate recommendations       │ │
│  │  4. Store report                   │ │
│  │  5. Create visualizations          │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 4. Storage Layer
```
┌─────────────────────────────────────────┐
│          PostgreSQL Database             │
│  ┌────────────────────────────────────┐ │
│  │  Tables:                           │ │
│  │  • traffic_data (all events)       │ │
│  │  • critical_traffic_alerts         │ │
│  │  • daily_traffic_reports           │ │
│  │                                    │ │
│  │  Views:                            │ │
│  │  • latest_traffic_status           │ │
│  │  • hourly_traffic_summary          │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 5. Serving Layer
```
┌─────────────────────────────────────────┐
│         Reports & Analytics              │
│  ┌────────────────────────────────────┐ │
│  │  Generated Outputs:                │ │
│  │  • PNG Charts (heatmaps, plots)    │ │
│  │  • CSV Reports                     │ │
│  │  • Intervention Recommendations    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Color Coding Recommendations

- **Blue**: Data sources and producers
- **Green**: Real-time processing (Kafka, Spark)
- **Orange**: Batch processing (Airflow)
- **Purple**: Storage layer (PostgreSQL)
- **Red**: Critical alerts and monitoring
- **Yellow**: Reports and outputs

## Data Flow Arrows

Use different arrow styles to show:
- **Solid arrows**: Real-time data flow
- **Dashed arrows**: Scheduled batch jobs
- **Bold arrows**: Critical alert paths
- **Bidirectional arrows**: Read/write operations

## Example Text for Diagram

Add these labels to show data characteristics:

**Kafka Input:**
```
{
  "sensor_id": "J1_Galle_Road",
  "timestamp": "2026-01-06T08:30:45",
  "vehicle_count": 220,
  "avg_speed": 8,
  "congestion_index": 27.5
}
Frequency: 4 msgs/sec
Volume: ~345K records/day
```

**Spark Processing:**
```
Window Size: 5 minutes
Watermark: 10 minutes
Latency: <5 seconds
Throughput: 240 msgs/min
```

**Airflow Schedule:**
```
Trigger: Daily @ 23:59
Duration: ~3 minutes
Output: PNG + CSV
```

## Diagram Layout Suggestions

1. **Top-to-Bottom Flow** (Recommended)
   - Sensors at top
   - Kafka in middle
   - Spark/Airflow processing
   - PostgreSQL storage
   - Reports at bottom

2. **Left-to-Right Flow** (Alternative)
   - Sensors on left
   - Processing in center
   - Storage and reports on right

## Tools and Dimensions

- **Canvas Size**: 1920x1080 pixels (for presentations)
- **Export Format**: PNG (high resolution, 300 DPI)
- **Color Scheme**: Use consistent colors matching your report theme
- **Font**: Use readable fonts (Arial, Calibri, or similar)
- **Icon Library**: Use icons for clarity (database icon, server icon, etc.)

## Example Draw.io Template

1. Open https://app.diagrams.net/
2. Create new diagram
3. Use shapes from:
   - **General**: Rectangles, rounded rectangles
   - **Cloud**: For Kafka, Spark
   - **Database**: For PostgreSQL
   - **Arrows**: Connectors with labels
4. Save as PNG and PDF for submission

## Final Checklist

- [ ] All 4 junctions clearly shown
- [ ] Kafka topic labeled
- [ ] Spark Streaming windows indicated
- [ ] Airflow DAG schedule visible
- [ ] PostgreSQL tables listed
- [ ] Data flow direction clear
- [ ] Lambda architecture layers distinguished
- [ ] Legend included (if using colors/symbols)
- [ ] Professional appearance (aligned, consistent fonts)

---

## Sample ASCII Architecture (for reference)

```
┌─────────────────┐
│ Traffic Sensors │ (4 Junctions: J1-J4)
│ Python Producers│ Every 2 seconds
└────────┬────────┘
         │ {sensor_id, timestamp, vehicle_count, avg_speed}
         ▼
┌─────────────────┐
│  Apache Kafka   │ Topic: traffic-data
│  (Zookeeper)    │ Partitions: 4, Retention: 24h
└────────┬────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼ SPEED LAYER                      ▼ (Optional)
┌─────────────────┐                  ┌──────────────┐
│ Spark Streaming │                  │ Kafka Console│
│ PySpark 3.5.0   │                  │  Consumer    │
└────────┬────────┘                  └──────────────┘
         │
         ├─ 5-min Windows → Congestion Index
         ├─ Filter (speed<10) → Critical Alerts
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ JDBC Write
│   trafficdb     │ Tables: traffic_data, critical_alerts
└────────┬────────┘
         │
         ▼ BATCH LAYER
┌─────────────────┐
│ Apache Airflow  │ Nightly @ 23:59
│  DAG Pipeline   │ Tasks: Extract → Analyze → Report
└────────┬────────┘
         │
         ▼ SERVING LAYER
┌─────────────────┐
│ Reports Folder  │ PNG Charts + CSV
│ Visualizations  │ Matplotlib/Seaborn
└─────────────────┘
```

Use this as reference when creating your professional diagram in draw.io or similar tools.
