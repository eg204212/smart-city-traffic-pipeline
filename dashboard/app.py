"""
Smart City Traffic Dashboard
Real-time visualization and monitoring interface
"""
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'postgres',
    'database': 'trafficdb',
    'user': 'airflow',
    'password': 'airflow'
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/current-status')
def current_status():
    """Get current traffic status for all junctions"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT DISTINCT ON (sensor_id)
            sensor_id,
            event_time,
            vehicle_count,
            avg_speed,
            congestion_index,
            traffic_status
        FROM traffic_data
        ORDER BY sensor_id, event_time DESC
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(row) for row in data])

@app.route('/api/hourly-stats')
def hourly_stats():
    """Get hourly statistics for today"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            sensor_id,
            hour_of_day,
            AVG(vehicle_count)::int as avg_vehicles,
            AVG(avg_speed)::int as avg_speed,
            AVG(congestion_index)::numeric(10,2) as avg_congestion,
            SUM(CASE WHEN traffic_status THEN 1 ELSE 0 END) as critical_count
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE
        GROUP BY sensor_id, hour_of_day
        ORDER BY sensor_id, hour_of_day
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(row) for row in data])

@app.route('/api/critical-alerts')
def critical_alerts():
    """Get recent critical traffic alerts"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            sensor_id,
            event_time,
            vehicle_count,
            avg_speed,
            congestion_index
        FROM critical_traffic_alerts
        ORDER BY event_time DESC
        LIMIT 50
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(row) for row in data])

@app.route('/api/daily-reports')
def daily_reports():
    """Get daily traffic reports"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            report_date,
            sensor_id,
            peak_hour,
            peak_hour_vehicle_count,
            total_daily_vehicles,
            avg_daily_speed::numeric(10,2) as avg_daily_speed,
            total_critical_alerts,
            requires_intervention
        FROM daily_traffic_reports
        ORDER BY report_date DESC, sensor_id
        LIMIT 20
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(row) for row in data])

@app.route('/api/stats-summary')
def stats_summary():
    """Get overall statistics summary"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Total records today
    cur.execute("""
        SELECT COUNT(*) as total_records
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE
    """)
    total_records = cur.fetchone()['total_records']
    
    # Critical alerts today
    cur.execute("""
        SELECT COUNT(*) as critical_alerts
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE AND traffic_status = TRUE
    """)
    critical_alerts = cur.fetchone()['critical_alerts']
    
    # Average speed today
    cur.execute("""
        SELECT AVG(avg_speed)::int as avg_speed
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE
    """)
    avg_speed = cur.fetchone()['avg_speed'] or 0
    
    # Peak junction today
    cur.execute("""
        SELECT sensor_id, SUM(vehicle_count) as total_vehicles
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE
        GROUP BY sensor_id
        ORDER BY total_vehicles DESC
        LIMIT 1
    """)
    peak_result = cur.fetchone()
    peak_junction = peak_result['sensor_id'] if peak_result else 'N/A'
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_records': total_records,
        'critical_alerts': critical_alerts,
        'avg_speed': avg_speed,
        'peak_junction': peak_junction
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
