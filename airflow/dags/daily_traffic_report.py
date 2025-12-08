from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2

def generate_report():
    conn = psycopg2.connect(
        dbname="trafficdb", user="airflow", password="airflow", host="postgres"
    )
    df = pd.read_sql("SELECT * FROM traffic_data;", conn)

    report = df.groupby(["sensor_id", df.timestamp.dt.hour])["vehicle_count"].sum()

    report.to_csv("/opt/airflow/reports/daily_report.csv")
    conn.close()

default_args = {
    'start_date': datetime(2025, 1, 1)
}

with DAG(
    "daily_traffic_report",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    task = PythonOperator(
        task_id="generate_report",
        python_callable=generate_report
    )
