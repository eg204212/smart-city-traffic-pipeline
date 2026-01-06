"""
Validation Script for Smart City Traffic System
Tests all components to ensure proper setup
"""
import psycopg2
import time
import sys

# Configuration
DB_CONFIG = {
    'dbname': 'trafficdb',
    'user': 'airflow',
    'password': 'airflow',
    'host': 'localhost',
    'port': 5432
}

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_database_connection():
    """Test PostgreSQL connection"""
    print_section("1. Testing PostgreSQL Connection")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Successfully connected to PostgreSQL")
        
        # Check tables
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_traffic_data():
    """Check if traffic data is being ingested"""
    print_section("2. Checking Traffic Data Ingestion")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM traffic_data;")
        count = cursor.fetchone()[0]
        print(f"📈 Total records in traffic_data: {count:,}")
        
        if count > 0:
            # Show latest records
            cursor.execute("""
                SELECT sensor_id, event_time, vehicle_count, avg_speed, congestion_index
                FROM traffic_data
                ORDER BY event_time DESC
                LIMIT 5;
            """)
            records = cursor.fetchall()
            
            print("\n🕒 Latest 5 records:")
            print(f"{'Sensor':<20} {'Time':<25} {'Vehicles':<10} {'Speed':<10} {'Cong.Idx':<10}")
            print("-" * 80)
            for record in records:
                print(f"{record[0]:<20} {str(record[1]):<25} {record[2]:<10} {record[3]:<10} {record[4]:<10.2f}")
            
            print(f"\n✅ Data is flowing! {count} records collected.")
        else:
            print("⚠️ No data yet. Producer may not be running or just started.")
        
        conn.close()
        return count > 0
    except Exception as e:
        print(f"❌ Error checking traffic data: {e}")
        return False

def check_critical_alerts():
    """Check critical traffic alerts"""
    print_section("3. Checking Critical Traffic Alerts")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM critical_traffic_alerts;")
        count = cursor.fetchone()[0]
        print(f"🚨 Total critical alerts: {count:,}")
        
        if count > 0:
            # Show recent alerts
            cursor.execute("""
                SELECT sensor_id, event_time, avg_speed, vehicle_count
                FROM critical_traffic_alerts
                ORDER BY event_time DESC
                LIMIT 5;
            """)
            alerts = cursor.fetchall()
            
            print("\n🔴 Recent critical alerts (speed < 10 km/h):")
            print(f"{'Sensor':<20} {'Time':<25} {'Speed':<10} {'Vehicles':<10}")
            print("-" * 70)
            for alert in alerts:
                print(f"{alert[0]:<20} {str(alert[1]):<25} {alert[2]:<10} {alert[3]:<10}")
            
            print(f"\n✅ Alerts are being captured!")
        else:
            print("ℹ️ No critical alerts yet (all traffic flowing normally).")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking alerts: {e}")
        return False

def check_hourly_statistics():
    """Show hourly traffic statistics"""
    print_section("4. Hourly Traffic Statistics")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                hour_of_day,
                COUNT(*) as records,
                AVG(vehicle_count) as avg_vehicles,
                AVG(avg_speed) as avg_speed,
                AVG(congestion_index) as avg_congestion
            FROM traffic_data
            GROUP BY hour_of_day
            ORDER BY hour_of_day DESC
            LIMIT 5;
        """)
        stats = cursor.fetchall()
        
        if stats:
            print("\n📊 Traffic statistics by hour:")
            print(f"{'Hour':<6} {'Records':<10} {'Avg Vehicles':<15} {'Avg Speed':<12} {'Avg Cong.':<12}")
            print("-" * 65)
            for stat in stats:
                print(f"{stat[0]:02d}:00  {stat[1]:<10} {stat[2]:<15.1f} {stat[3]:<12.1f} {stat[4]:<12.2f}")
            print("\n✅ Hourly aggregations working!")
        else:
            print("ℹ️ Not enough data for hourly statistics yet.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking statistics: {e}")
        return False

def check_junction_summary():
    """Show summary by junction"""
    print_section("5. Junction Summary")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sensor_id,
                COUNT(*) as total_records,
                AVG(vehicle_count) as avg_vehicles,
                AVG(avg_speed) as avg_speed,
                MIN(avg_speed) as min_speed,
                MAX(vehicle_count) as max_vehicles,
                SUM(CASE WHEN traffic_status THEN 1 ELSE 0 END) as critical_count
            FROM traffic_data
            GROUP BY sensor_id
            ORDER BY sensor_id;
        """)
        summary = cursor.fetchall()
        
        if summary:
            print("\n🚦 Summary by junction:")
            print(f"{'Junction':<22} {'Records':<10} {'Avg Veh':<10} {'Avg Spd':<10} {'Min Spd':<10} {'Max Veh':<10} {'Alerts':<8}")
            print("-" * 90)
            for row in summary:
                print(f"{row[0]:<22} {row[1]:<10} {row[2]:<10.1f} {row[3]:<10.1f} {row[4]:<10} {row[5]:<10} {row[6]:<8}")
            print("\n✅ All junctions reporting!")
        else:
            print("ℹ️ No junction data available yet.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking junctions: {e}")
        return False

def main():
    """Run all validation checks"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█  Smart City Traffic System - Validation Script  █")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = []
    
    # Run checks
    results.append(("Database Connection", check_database_connection()))
    time.sleep(1)
    
    results.append(("Traffic Data Ingestion", check_traffic_data()))
    time.sleep(1)
    
    results.append(("Critical Alerts", check_critical_alerts()))
    time.sleep(1)
    
    results.append(("Hourly Statistics", check_hourly_statistics()))
    time.sleep(1)
    
    results.append(("Junction Summary", check_junction_summary()))
    
    # Summary
    print_section("Validation Summary")
    print()
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All systems operational! Your pipeline is working correctly.")
        print("\nNext steps:")
        print("1. View live logs: docker logs -f traffic-producer")
        print("2. Access Airflow UI: http://localhost:8085 (admin/admin)")
        print("3. Run manual report: python reports/generate_report.py")
    else:
        print("\n⚠️ Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all containers are running: docker-compose ps")
        print("2. Check logs: docker logs traffic-producer")
        print("3. Restart services: docker-compose restart")
    
    print("\n" + "█"*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
