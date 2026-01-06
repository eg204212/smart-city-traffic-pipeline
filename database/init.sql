-- Smart City Traffic Database Schema
-- Initialize PostgreSQL database with required tables

-- Main traffic data table (populated by Spark streaming)
CREATE TABLE IF NOT EXISTS traffic_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    vehicle_count INTEGER NOT NULL,
    avg_speed INTEGER NOT NULL,
    congestion_index DOUBLE PRECISION,
    traffic_status BOOLEAN,
    hour_of_day INTEGER,
    processing_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_traffic_event_time ON traffic_data(event_time);
CREATE INDEX idx_traffic_sensor ON traffic_data(sensor_id);
CREATE INDEX idx_traffic_hour ON traffic_data(hour_of_day);

-- Critical traffic alerts table
CREATE TABLE IF NOT EXISTS critical_traffic_alerts (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    vehicle_count INTEGER NOT NULL,
    avg_speed INTEGER NOT NULL,
    congestion_index DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_event_time ON critical_traffic_alerts(event_time);
CREATE INDEX idx_alerts_sensor ON critical_traffic_alerts(sensor_id);

-- Daily traffic reports table (populated by Airflow)
CREATE TABLE IF NOT EXISTS daily_traffic_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    peak_hour INTEGER,
    peak_hour_vehicle_count INTEGER,
    total_daily_vehicles INTEGER,
    avg_daily_speed DOUBLE PRECISION,
    total_critical_alerts INTEGER,
    requires_intervention BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, sensor_id)
);

CREATE INDEX idx_reports_date ON daily_traffic_reports(report_date);

-- View: Latest traffic status by junction
CREATE OR REPLACE VIEW latest_traffic_status AS
SELECT DISTINCT ON (sensor_id)
    sensor_id,
    event_time,
    vehicle_count,
    avg_speed,
    congestion_index,
    traffic_status
FROM traffic_data
ORDER BY sensor_id, event_time DESC;

-- View: Hourly traffic summary
CREATE OR REPLACE VIEW hourly_traffic_summary AS
SELECT 
    sensor_id,
    DATE(event_time) as traffic_date,
    hour_of_day,
    COUNT(*) as record_count,
    AVG(vehicle_count) as avg_vehicles,
    AVG(avg_speed) as avg_speed,
    AVG(congestion_index) as avg_congestion,
    SUM(CASE WHEN traffic_status THEN 1 ELSE 0 END) as critical_count
FROM traffic_data
GROUP BY sensor_id, DATE(event_time), hour_of_day
ORDER BY traffic_date DESC, hour_of_day;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO airflow;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO airflow;
