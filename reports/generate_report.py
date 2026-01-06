"""
Manual Report Generator
Can be run independently to generate reports from stored data
"""
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Database connection
DB_CONFIG = {
    'dbname': 'trafficdb',
    'user': 'airflow',
    'password': 'airflow',
    'host': 'localhost',
    'port': 5432
}

def get_traffic_data(days=7):
    """Fetch traffic data from PostgreSQL"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = f"""
        SELECT 
            sensor_id,
            event_time,
            vehicle_count,
            avg_speed,
            congestion_index,
            traffic_status,
            hour_of_day
        FROM traffic_data
        WHERE event_time >= NOW() - INTERVAL '{days} days'
        ORDER BY event_time;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df

def get_critical_alerts(days=7):
    """Fetch critical traffic alerts"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = f"""
        SELECT * FROM critical_traffic_alerts
        WHERE event_time >= NOW() - INTERVAL '{days} days'
        ORDER BY event_time DESC;
    """
    
    alerts_df = pd.read_sql(query, conn)
    conn.close()
    
    return alerts_df

def generate_comprehensive_report(output_dir='reports'):
    """Generate comprehensive traffic analysis report"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("📊 Generating Comprehensive Traffic Report...")
    
    # Fetch data
    df = get_traffic_data(days=7)
    alerts = get_critical_alerts(days=7)
    
    if df.empty:
        print("❌ No data available")
        return
    
    # Convert timestamp
    df['event_time'] = pd.to_datetime(df['event_time'])
    
    # Create comprehensive visualization
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Traffic Volume Over Time (All Junctions)
    ax1 = fig.add_subplot(gs[0, :])
    for junction in df['sensor_id'].unique():
        junction_data = df[df['sensor_id'] == junction]
        hourly = junction_data.set_index('event_time').resample('1H')['vehicle_count'].sum()
        ax1.plot(hourly.index, hourly.values, marker='o', label=junction, linewidth=2)
    ax1.set_title('Traffic Volume Over Time (Hourly)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Total Vehicles')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Average Speed by Junction
    ax2 = fig.add_subplot(gs[1, 0])
    avg_speeds = df.groupby('sensor_id')['avg_speed'].mean().sort_values()
    colors = ['red' if x < 15 else 'orange' if x < 25 else 'green' for x in avg_speeds]
    ax2.barh(avg_speeds.index, avg_speeds.values, color=colors)
    ax2.set_xlabel('Average Speed (km/h)')
    ax2.set_title('Average Speed by Junction')
    ax2.axvline(x=10, color='red', linestyle='--', label='Critical Threshold')
    ax2.legend()
    
    # 3. Congestion Index Distribution
    ax3 = fig.add_subplot(gs[1, 1])
    df.boxplot(column='congestion_index', by='sensor_id', ax=ax3)
    ax3.set_title('Congestion Index Distribution')
    ax3.set_xlabel('Junction')
    ax3.set_ylabel('Congestion Index')
    plt.suptitle('')  # Remove automatic title
    
    # 4. Critical Alerts Count
    ax4 = fig.add_subplot(gs[1, 2])
    alert_counts = alerts.groupby('sensor_id').size().sort_values(ascending=False)
    ax4.bar(alert_counts.index, alert_counts.values, color='red', alpha=0.7)
    ax4.set_title('Critical Alerts by Junction')
    ax4.set_xlabel('Junction')
    ax4.set_ylabel('Number of Alerts')
    ax4.tick_params(axis='x', rotation=45)
    
    # 5. Hourly Traffic Pattern (Heatmap)
    ax5 = fig.add_subplot(gs[2, :2])
    pivot = df.groupby(['sensor_id', 'hour_of_day'])['vehicle_count'].mean().reset_index()
    pivot_table = pivot.pivot(index='sensor_id', columns='hour_of_day', values='vehicle_count')
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax5, cbar_kws={'label': 'Avg Vehicles'})
    ax5.set_title('Average Vehicle Count Heatmap (Hour vs Junction)')
    ax5.set_xlabel('Hour of Day')
    ax5.set_ylabel('Junction')
    
    # 6. Speed Distribution
    ax6 = fig.add_subplot(gs[2, 2])
    df['avg_speed'].hist(bins=30, ax=ax6, color='skyblue', edgecolor='black')
    ax6.axvline(x=10, color='red', linestyle='--', linewidth=2, label='Critical Speed')
    ax6.set_title('Speed Distribution')
    ax6.set_xlabel('Speed (km/h)')
    ax6.set_ylabel('Frequency')
    ax6.legend()
    
    # Main title
    fig.suptitle(f'Smart City Traffic Analysis Report - Last 7 Days', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    # Save figure
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f'traffic_report_{timestamp}.png')
    plt.savefig(report_path, dpi=300, bbox_inches='tight')
    print(f"✅ Report saved: {report_path}")
    
    # Generate summary statistics
    summary_path = os.path.join(output_dir, f'traffic_summary_{timestamp}.txt')
    with open(summary_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("SMART CITY TRAFFIC ANALYSIS SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Report Period: {df['event_time'].min()} to {df['event_time'].max()}\n")
        f.write(f"Total Records: {len(df):,}\n")
        f.write(f"Total Critical Alerts: {len(alerts):,}\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("JUNCTION STATISTICS\n")
        f.write("-" * 60 + "\n")
        
        for junction in df['sensor_id'].unique():
            junc_data = df[df['sensor_id'] == junction]
            junc_alerts = alerts[alerts['sensor_id'] == junction]
            
            f.write(f"\n{junction}:\n")
            f.write(f"  Total Vehicles: {junc_data['vehicle_count'].sum():,}\n")
            f.write(f"  Average Speed: {junc_data['avg_speed'].mean():.1f} km/h\n")
            f.write(f"  Average Congestion Index: {junc_data['congestion_index'].mean():.2f}\n")
            f.write(f"  Critical Alerts: {len(junc_alerts)}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"✅ Summary saved: {summary_path}")
    
    # Generate CSV export
    csv_path = os.path.join(output_dir, f'traffic_data_export_{timestamp}.csv')
    df.to_csv(csv_path, index=False)
    print(f"✅ Data exported: {csv_path}")
    
    plt.show()

if __name__ == "__main__":
    generate_comprehensive_report()
