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
    'host': '127.0.0.1',
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

def generate_comprehensive_report(output_dir=None):
    """Generate comprehensive traffic analysis report"""
    
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

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
    
    # Set style for better visuals
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Create comprehensive visualization with better spacing
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3, top=0.94, bottom=0.06, left=0.06, right=0.96)
    
    # 1. Traffic Volume Over Time (All Junctions)
    ax1 = fig.add_subplot(gs[0, :])
    for junction in sorted(df['sensor_id'].unique()):
        junction_data = df[df['sensor_id'] == junction]
        hourly = junction_data.set_index('event_time').resample('1h')['vehicle_count'].sum()
        ax1.plot(hourly.index, hourly.values, marker='o', label=junction.replace('_', ' '), 
                linewidth=2, markersize=4)
    ax1.set_title('Traffic Volume vs Time (Hourly Aggregation)', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Time', fontsize=11)
    ax1.set_ylabel('Total Vehicles', fontsize=11)
    ax1.legend(loc='upper left', frameon=True, fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.tick_params(axis='x', rotation=30)
    
    # 2. Average Speed by Junction
    ax2 = fig.add_subplot(gs[1, 0])
    avg_speeds = df.groupby('sensor_id')['avg_speed'].mean().sort_values()
    colors = ['#d62728' if x < 15 else '#ff7f0e' if x < 25 else '#2ca02c' for x in avg_speeds]
    bars = ax2.barh(range(len(avg_speeds)), avg_speeds.values, color=colors, edgecolor='black', linewidth=0.7)
    ax2.set_yticks(range(len(avg_speeds)))
    ax2.set_yticklabels([label.replace('_', ' ') for label in avg_speeds.index], fontsize=10)
    ax2.set_xlabel('Average Speed (km/h)', fontsize=11)
    ax2.set_title('Average Speed by Junction', fontsize=13, fontweight='bold', pad=10)
    ax2.axvline(x=10, color='red', linestyle='--', linewidth=2, label='Critical (<10 km/h)', alpha=0.7)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='x')
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, avg_speeds.values)):
        ax2.text(val + 1, i, f'{val:.1f}', va='center', fontsize=9)
    
    # 3. Critical Alerts Count
    ax3 = fig.add_subplot(gs[1, 1])
    if not alerts.empty:
        alert_counts = alerts.groupby('sensor_id').size().sort_values(ascending=False)
        bars = ax3.bar(range(len(alert_counts)), alert_counts.values, color='#d62728', 
                      alpha=0.7, edgecolor='black', linewidth=0.7)
        ax3.set_xticks(range(len(alert_counts)))
        ax3.set_xticklabels([label.replace('_', '\n') for label in alert_counts.index], 
                           fontsize=9, rotation=0)
        ax3.set_ylabel('Number of Alerts', fontsize=11)
        ax3.set_title('Critical Traffic Alerts (Speed < 10 km/h)', fontsize=13, fontweight='bold', pad=10)
        ax3.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bar, val in zip(bars, alert_counts.values):
            ax3.text(bar.get_x() + bar.get_width()/2, val + 1, str(int(val)), 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'No Critical Alerts', ha='center', va='center', 
                fontsize=14, transform=ax3.transAxes)
        ax3.set_title('Critical Traffic Alerts', fontsize=13, fontweight='bold', pad=10)
    
    # 4. Hourly Traffic Pattern (Heatmap)
    ax4 = fig.add_subplot(gs[2, :])
    pivot = df.groupby(['sensor_id', 'hour_of_day'])['vehicle_count'].mean().reset_index()
    pivot_table = pivot.pivot(index='sensor_id', columns='hour_of_day', values='vehicle_count')
    pivot_table.index = [idx.replace('_', ' ') for idx in pivot_table.index]
    
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax4, 
               cbar_kws={'label': 'Avg Vehicles'}, linewidths=0.5, linecolor='gray',
               annot_kws={'fontsize': 8})
    ax4.set_title('Traffic Volume Heatmap: Junction vs Hour of Day', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xlabel('Hour of Day (0-23)', fontsize=11)
    ax4.set_ylabel('Junction', fontsize=11)
    ax4.tick_params(axis='x', labelsize=9)
    ax4.tick_params(axis='y', labelsize=10, rotation=0)
    
    # Main title
    fig.suptitle('Smart City Traffic Analysis Dashboard', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Save figure with high quality
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f'traffic_report_{timestamp}.png')
    plt.savefig(report_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✅ Report saved: {report_path}")
    plt.close()
    
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
    
    print("\n" + "="*60)
    print("📊 Report Generation Complete!")
    print("="*60)

if __name__ == "__main__":
    generate_comprehensive_report()
