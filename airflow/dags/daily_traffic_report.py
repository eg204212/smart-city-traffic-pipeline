"""
Smart City Daily Traffic Analysis DAG
Scheduled to run nightly at 11:59 PM
- Analyzes peak traffic hours per junction
- Identifies junctions requiring police intervention
- Generates comprehensive daily report
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

# DAG default arguments
default_args = {
    'owner': 'smart_city_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def extract_traffic_data(**context):
    """Extract yesterday's traffic data from PostgreSQL"""
    logger.info("📥 Extracting traffic data from PostgreSQL...")
    
    hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Get yesterday's data
    query = """
        SELECT 
            sensor_id,
            event_time,
            vehicle_count,
            avg_speed,
            congestion_index,
            traffic_status,
            hour_of_day
        FROM traffic_data
        WHERE DATE(event_time) = CURRENT_DATE - INTERVAL '1 day'
        ORDER BY event_time;
    """
    
    df = hook.get_pandas_df(query)
    logger.info(f"✅ Extracted {len(df)} records")
    
    # Save to XCom for next task
    context['ti'].xcom_push(key='traffic_data_count', value=len(df))
    
    return df.to_json()

def analyze_peak_hours(**context):
    """Identify peak traffic hour for each junction"""
    logger.info("📊 Analyzing peak traffic hours...")
    
    # Get data from previous task
    traffic_json = context['ti'].xcom_pull(task_ids='extract_traffic_data')
    df = pd.read_json(traffic_json)
    
    if df.empty:
        logger.warning("⚠️ No data available for analysis")
        return None
    
    # Convert timestamp
    df['event_time'] = pd.to_datetime(df['event_time'])
    
    # Group by junction and hour to find peak traffic
    hourly_stats = df.groupby(['sensor_id', 'hour_of_day']).agg({
        'vehicle_count': ['sum', 'mean'],
        'avg_speed': 'mean',
        'congestion_index': 'mean',
        'traffic_status': 'sum'  # Count critical alerts
    }).reset_index()
    
    hourly_stats.columns = [
        'sensor_id', 'hour', 'total_vehicles', 'avg_vehicles',
        'avg_speed', 'avg_congestion', 'critical_alerts'
    ]
    
    # Find peak hour for each junction
    peak_hours = hourly_stats.loc[
        hourly_stats.groupby('sensor_id')['total_vehicles'].idxmax()
    ]
    
    logger.info("🏆 Peak hours identified:")
    for _, row in peak_hours.iterrows():
        logger.info(
            f"  {row['sensor_id']}: {row['hour']:02d}:00 "
            f"({int(row['total_vehicles'])} vehicles)"
        )
    
    context['ti'].xcom_push(key='peak_hours', value=peak_hours.to_json())
    return hourly_stats.to_json()

def generate_intervention_recommendations(**context):
    """Determine which junctions need police intervention"""
    logger.info("🚓 Generating intervention recommendations...")
    
    peak_hours_json = context['ti'].xcom_pull(task_ids='analyze_peak_hours', key='peak_hours')
    peak_hours = pd.read_json(peak_hours_json)
    
    # Criteria for intervention:
    # 1. High congestion index (> 5.0)
    # 2. Multiple critical alerts (> 10)
    # 3. High vehicle count with low speed
    
    recommendations = []
    for _, row in peak_hours.iterrows():
        needs_intervention = False
        reasons = []
        
        if row['avg_congestion'] > 5.0:
            needs_intervention = True
            reasons.append(f"High congestion index: {row['avg_congestion']:.2f}")
        
        if row['critical_alerts'] > 10:
            needs_intervention = True
            reasons.append(f"Multiple alerts: {int(row['critical_alerts'])}")
        
        if row['avg_speed'] < 15:
            needs_intervention = True
            reasons.append(f"Low average speed: {row['avg_speed']:.1f} km/h")
        
        recommendations.append({
            'sensor_id': row['sensor_id'],
            'peak_hour': int(row['hour']),
            'requires_intervention': needs_intervention,
            'priority': 'HIGH' if needs_intervention else 'LOW',
            'reasons': ' | '.join(reasons) if reasons else 'Normal traffic flow'
        })
    
    rec_df = pd.DataFrame(recommendations)
    logger.info(f"⚠️ Junctions requiring intervention: {rec_df['requires_intervention'].sum()}")
    
    context['ti'].xcom_push(key='recommendations', value=rec_df.to_json())
    return rec_df.to_json()

def store_daily_report(**context):
    """Store analysis results in daily_traffic_reports table"""
    logger.info("💾 Storing daily report...")
    
    peak_hours_json = context['ti'].xcom_pull(task_ids='analyze_peak_hours', key='peak_hours')
    recommendations_json = context['ti'].xcom_pull(task_ids='generate_recommendations', key='recommendations')
    
    peak_hours = pd.read_json(peak_hours_json)
    recommendations = pd.read_json(recommendations_json)
    
    # Merge data
    report = peak_hours.merge(recommendations[['sensor_id', 'requires_intervention']], on='sensor_id')
    
    # Get traffic data for daily totals
    traffic_json = context['ti'].xcom_pull(task_ids='extract_traffic_data')
    df = pd.read_json(traffic_json)
    
    daily_totals = df.groupby('sensor_id').agg({
        'vehicle_count': 'sum',
        'avg_speed': 'mean'
    }).reset_index()
    
    report = report.merge(daily_totals, on='sensor_id')
    
    # Prepare for database insert
    hook = PostgresHook(postgres_conn_id='postgres_default')
    
    for _, row in report.iterrows():
        insert_query = """
            INSERT INTO daily_traffic_reports 
            (report_date, sensor_id, peak_hour, peak_hour_vehicle_count, 
             total_daily_vehicles, avg_daily_speed, total_critical_alerts, requires_intervention)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (report_date, sensor_id) DO UPDATE SET
                peak_hour = EXCLUDED.peak_hour,
                peak_hour_vehicle_count = EXCLUDED.peak_hour_vehicle_count,
                total_daily_vehicles = EXCLUDED.total_daily_vehicles,
                avg_daily_speed = EXCLUDED.avg_daily_speed,
                total_critical_alerts = EXCLUDED.total_critical_alerts,
                requires_intervention = EXCLUDED.requires_intervention;
        """
        
        hook.run(insert_query, parameters=(
            datetime.now().date() - timedelta(days=1),
            row['sensor_id'],
            int(row['hour']),
            int(row['total_vehicles']),
            int(row['vehicle_count']),
            float(row['avg_speed']),
            int(row['critical_alerts']),
            bool(row['requires_intervention'])
        ))
    
    logger.info("✅ Daily report stored successfully")

def generate_csv_report(**context):
    """Generate CSV report with traffic analysis"""
    logger.info("📄 Generating CSV report...")
    
    # Get data
    recommendations_json = context['ti'].xcom_pull(task_ids='generate_recommendations', key='recommendations')
    recommendations = pd.read_json(recommendations_json)
    
    # Create reports directory if it doesn't exist
    os.makedirs('/opt/airflow/reports', exist_ok=True)
    
    # Generate CSV report
    csv_path = f'/opt/airflow/reports/daily_traffic_report_{datetime.now().strftime("%Y%m%d")}.csv'
    recommendations.to_csv(csv_path, index=False)
    logger.info(f"✅ CSV report saved: {csv_path}")
    
    return csv_path

# Define the DAG
with DAG(
    'smart_city_daily_traffic_report',
    default_args=default_args,
    description='Daily traffic analysis and reporting pipeline',
    schedule_interval='59 23 * * *',  # Run at 11:59 PM every night
    catchup=False,
    tags=['traffic', 'smart-city', 'batch-processing'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_traffic_data',
        python_callable=extract_traffic_data,
        provide_context=True,
    )

    analyze_task = PythonOperator(
        task_id='analyze_peak_hours',
        python_callable=analyze_peak_hours,
        provide_context=True,
    )

    recommendations_task = PythonOperator(
        task_id='generate_recommendations',
        python_callable=generate_intervention_recommendations,
        provide_context=True,
    )

    store_task = PythonOperator(
        task_id='store_daily_report',
        python_callable=store_daily_report,
        provide_context=True,
    )

    csv_report_task = PythonOperator(
        task_id='generate_csv_report',
        python_callable=generate_csv_report,
        provide_context=True,
    )

    # Define task dependencies
    extract_task >> analyze_task >> recommendations_task >> [store_task, csv_report_task]

