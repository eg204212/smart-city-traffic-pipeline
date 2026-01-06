# 🚀 Complete Step-by-Step Running Guide

## Current Status ✅

Your project has the following services running:
- ✅ **Zookeeper**: Running on port 2181
- ✅ **PostgreSQL**: Running on port 5432
- ✅ **Airflow Webserver**: Running on port 8085
- ✅ **Airflow Scheduler**: Running
- ✅ **Spark Master**: Running on port 8080
- ⚠️ **Kafka**: Needs configuration fix
- ⚠️ **Spark Worker**: Exited (needs restart)
- ⚠️ **Producer**: Not running yet

---

## 📝 Step-by-Step Instructions

### Step 1: Check Current Container Status

```powershell
cd "d:\Semester 8\BigData\MiniProject\smart-city-traffic-project"
docker-compose ps
```

### Step 2: Restart Kafka with Fixed Configuration

```powershell
docker-compose down kafka
docker-compose up -d kafka
Start-Sleep -Seconds 15  # Wait for Kafka to start
```

### Step 3: Verify Kafka is Working

```powershell
docker logs kafka --tail 20
```

You should see logs like "INFO [KafkaServer id=1] started"

### Step 4: Create Kafka Topic Manually

```powershell
docker exec kafka kafka-topics.sh --create --topic traffic-data --bootstrap-server localhost:9092 --partitions 4 --replication-factor 1
```

### Step 5: Verify Topic Creation

```powershell
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

You should see `traffic-data` in the list.

### Step 6: Start the Traffic Producer (Simple Method)

Since we're running outside Docker, use this command:

```powershell
python producer\traffic_producer.py
```

**Expected Output:**
```
🚀 Starting Smart City Traffic Producer...
📡 Monitoring 4 junctions
🟢 NORMAL | J1_Galle_Road | Vehicles: 180 | Speed: 45 km/h | Index: 4.00
🔴 CRITICAL | J2_Duplication_Road | Vehicles: 220 | Speed: 8 km/h | Index: 27.50
...
```

### Step 7: Verify Data in Kafka (In Another Terminal)

```powershell
docker exec kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic traffic-data --from-beginning --max-messages 5
```

You should see JSON messages.

### Step 8: Check Database for Data

```powershell
docker exec -it postgres psql -U airflow -d trafficdb
```

Then run:
```sql
SELECT COUNT(*) FROM traffic_data;
SELECT * FROM traffic_data ORDER BY event_time DESC LIMIT 5;
\q
```

### Step 9: Access Web UIs

Open your browser and visit:

1. **Airflow**: http://localhost:8085
   - Username: `admin`
   - Password: `admin`
   
2. **Spark Master**: http://localhost:8080

### Step 10: Trigger Airflow DAG (After Data Collection)

1. Go to http://localhost:8085
2. Find DAG: `smart_city_daily_traffic_report`
3. Toggle it ON
4. Click "Trigger DAG" button
5. Watch the task execution

---

## 🔍 Validation Checklist

Run these commands to verify everything is working:

```powershell
# 1. Check all containers
docker-compose ps

# 2. Check traffic data count
docker exec postgres psql -U airflow -d trafficdb -c "SELECT COUNT(*) FROM traffic_data;"

# 3. Check critical alerts
docker exec postgres psql -U airflow -d trafficdb -c "SELECT COUNT(*) FROM critical_traffic_alerts;"

# 4. Check recent traffic
docker exec postgres psql -U airflow -d trafficdb -c "SELECT sensor_id, event_time, vehicle_count, avg_speed FROM traffic_data ORDER BY event_time DESC LIMIT 5;"
```

---

## 📊 Expected Results

After running for 5-10 minutes:

1. **Kafka Topic**: Should have hundreds of messages
2. **PostgreSQL**: 
   - `traffic_data` table: ~600+ records (4 junctions × 30 records/minute)
   - `critical_traffic_alerts` table: ~100+ records (15% critical rate)
3. **Producer Logs**: Clean output with colored status indicators
4. **Airflow**: DAG should be visible and executable

---

## 🐛 Troubleshooting

### Problem: Producer Can't Connect to Kafka

**Solution:**
```powershell
# Restart Kafka
docker-compose restart kafka
Start-Sleep -Seconds 20

# Verify Kafka is listening
docker exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Problem: No Data in Database

**Check if Spark job is running:**
```powershell
docker-compose logs traffic-stream-processor
```

If not running, start it:
```powershell
docker-compose up -d traffic-stream-processor
```

### Problem: Airflow DAG Not Visible

**Solution:**
```powershell
docker-compose restart airflow-scheduler
Start-Sleep -Seconds 10
docker logs airflow-scheduler | Select-String "ERROR"
```

---

## 📸 Screenshots to Take for Submission

1. **Producer Running**: Screenshot of terminal with traffic data flowing
2. **Kafka Messages**: Screenshot of console consumer showing JSON data
3. **Database Data**: Screenshot of PostgreSQL query results
4. **Airflow DAG**: Screenshot of Airflow UI showing the DAG
5. **Spark UI**: Screenshot of Spark Master UI
6. **Generated Report**: Screenshot of the PNG visualization

---

## 🎯 Quick Test Commands

```powershell
# Test 1: Producer is sending data
docker exec kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic traffic-data --max-messages 3

# Test 2: Database has data
docker exec postgres psql -U airflow -d trafficdb -c "SELECT COUNT(*) as total_records FROM traffic_data;"

# Test 3: Critical alerts are being detected
docker exec postgres psql -U airflow -d trafficdb -c "SELECT sensor_id, avg_speed, vehicle_count FROM critical_traffic_alerts LIMIT 5;"

# Test 4: Airflow is healthy
curl http://localhost:8085/health

# Test 5: Spark Master is running
curl http://localhost:8080
```

---

## 📈 Generating Final Report

Once you have data (after running for 1+ hours):

1. **Install Python dependencies:**
```powershell
pip install pandas matplotlib seaborn psycopg2-binary
```

2. **Run report generator:**
```powershell
python reports\generate_report.py
```

3. **Check generated files:**
```powershell
dir reports\*.png
dir reports\*.csv
```

---

## 🎓 For Demonstration/Submission

### Prepare Your Demo:

1. **Start all services** (if not already running)
2. **Run producer** for at least 30 minutes to collect data
3. **Trigger Airflow DAG** manually
4. **Generate visualizations**
5. **Take screenshots** of all components
6. **Export database** for backup:
   ```powershell
   docker exec postgres pg_dump -U airflow trafficdb > traffic_backup.sql
   ```

### Demo Script:

1. Show producer generating data (Terminal 1)
2. Show Kafka messages (Terminal 2)
3. Show database queries (Terminal 3)
4. Show Airflow UI in browser
5. Show Spark UI in browser
6. Show generated reports in reports/ folder

---

## ✅ Final Checklist Before Submission

- [ ] All containers running (`docker-compose ps`)
- [ ] Producer running and generating data
- [ ] Database has >1000 records
- [ ] Critical alerts table has data
- [ ] Airflow DAG visible and can be triggered
- [ ] Reports folder has PNG and CSV files
- [ ] All screenshots taken
- [ ] README.md reviewed
- [ ] PROJECT_REPORT.md completed
- [ ] Code comments are clear
- [ ] Architecture diagram created

---

**Need Help?**

If any step fails, check:
1. Docker Desktop is running
2. Ports are not in use by other applications
3. Sufficient RAM available (8GB minimum)
4. Windows Firewall not blocking ports

**Common Port Conflicts:**
- 8080 (Spark) - might conflict with other apps
- 5432 (PostgreSQL) - might have local PostgreSQL
- 9092 (Kafka) - usually free

Good luck with your demo! 🎉
