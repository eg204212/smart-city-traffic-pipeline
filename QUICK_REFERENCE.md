# 🚀 Quick Reference Card - Smart City Traffic System

## 🔧 Essential Commands

### Start the System
```powershell
# Windows (Recommended)
.\start.bat

# Manual start
docker-compose up -d
```

### Stop the System
```powershell
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove data
```

### View Logs
```powershell
docker logs -f traffic-producer           # Producer
docker logs -f traffic-stream-processor   # Spark
docker logs -f airflow-scheduler          # Airflow
docker logs -f kafka                      # Kafka
```

### Check Status
```powershell
docker-compose ps          # All containers
python validate_system.py  # Full system check
```

---

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8085 | admin / admin |
| Spark Master | http://localhost:8080 | - |
| Spark Worker | http://localhost:8081 | - |
| PostgreSQL | localhost:5432 | airflow / airflow |

---

## 💾 Database Queries

### Connect to PostgreSQL
```powershell
docker exec -it postgres psql -U airflow -d trafficdb
```

### Useful Queries
```sql
-- Total records
SELECT COUNT(*) FROM traffic_data;

-- Latest traffic
SELECT sensor_id, event_time, vehicle_count, avg_speed
FROM traffic_data ORDER BY event_time DESC LIMIT 10;

-- Critical alerts
SELECT * FROM critical_traffic_alerts 
ORDER BY event_time DESC LIMIT 10;

-- Hourly summary
SELECT * FROM hourly_traffic_summary LIMIT 20;

-- Daily reports
SELECT * FROM daily_traffic_reports 
WHERE report_date = CURRENT_DATE;
```

---

## 📊 Generate Reports

```powershell
# Manual report generation
python reports/generate_report.py

# Trigger Airflow DAG
docker exec airflow-scheduler airflow dags trigger smart_city_daily_traffic_report

# Check reports folder
dir reports\
```

---

## 🐛 Troubleshooting

### Restart Specific Service
```powershell
docker-compose restart kafka
docker-compose restart traffic-producer
docker-compose restart traffic-stream-processor
```

### Check Kafka Topics
```powershell
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

### View Kafka Messages
```powershell
docker exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic traffic-data \
  --from-beginning --max-messages 5
```

### Reset Everything
```powershell
docker-compose down -v
docker system prune -f
.\start.bat
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration |
| `producer/traffic_producer.py` | Data generator |
| `spark/traffic_stream.py` | Stream processing |
| `airflow/dags/daily_traffic_report.py` | Batch analytics |
| `database/init.sql` | Database schema |
| `README.md` | Full documentation |
| `PROJECT_REPORT.md` | Academic report |

---

## 🎯 Key Metrics

- **Junctions**: 4 (J1-J4)
- **Data Frequency**: Every 2 seconds
- **Messages/Day**: ~345,600
- **Window Size**: 5 minutes
- **Alert Threshold**: Speed < 10 km/h
- **Batch Schedule**: Daily @ 11:59 PM

---

## ✅ Pre-Submission Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] Data flowing to PostgreSQL (`python validate_system.py`)
- [ ] Reports generated (`reports/` folder)
- [ ] Architecture diagram created
- [ ] PROJECT_REPORT.md converted to PDF
- [ ] Code tested on fresh install
- [ ] README.md reviewed

---

## 📞 Quick Debugging

**No data in database?**
```powershell
docker logs traffic-producer  # Check producer
docker logs traffic-stream-processor  # Check Spark
```

**Airflow DAG not showing?**
```powershell
docker-compose restart airflow-scheduler
docker logs airflow-scheduler | grep ERROR
```

**Port conflicts?**
- Edit `docker-compose.yml` ports section
- Change `8085:8080` to `8086:8080` (for example)

---

**Last Updated**: January 6, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
