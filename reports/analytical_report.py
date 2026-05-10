"""
Analytical Report Generator for Smart City Traffic System
Generates submission-ready reports as per project requirements
"""
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages

# Database connection
DB_CONFIG = {
    'dbname': 'trafficdb',
    'user': 'airflow',
    'password': 'airflow',
    'host': 'localhost',
    'port': 5432
}

def get_traffic_data():
    """Fetch all traffic data from PostgreSQL"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
        SELECT 
            sensor_id,
            event_time,
            TO_CHAR(event_time, 'YYYY-MM-DD') as date,
            EXTRACT(HOUR FROM event_time) as hour_of_day,
            vehicle_count,
            avg_speed,
            congestion_index
        FROM traffic_data
        ORDER BY event_time;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df

def get_critical_alerts():
    """Fetch critical traffic alerts"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
        SELECT 
            sensor_id,
            event_time,
            vehicle_count,
            avg_speed,
            congestion_index
        FROM critical_traffic_alerts
        ORDER BY event_time;
    """
    
    alerts_df = pd.read_sql(query, conn)
    conn.close()
    
    return alerts_df

def generate_traffic_volume_vs_time():
    """
    PRIMARY REQUIREMENT: Traffic Volume vs. Time of Day
    This is the main analytical visualization required
    """
    print("📊 Generating Traffic Volume vs. Time of Day Analysis...")
    
    df = get_traffic_data()
    
    if df.empty:
        print("❌ No data available")
        return None
    
    # Aggregate traffic volume by hour and junction
    hourly_traffic = df.groupby(['hour_of_day', 'sensor_id'])['vehicle_count'].sum().reset_index()
    
    # Create the main analytical chart
    plt.figure(figsize=(16, 10))
    
    # Main plot: Traffic Volume vs Time of Day
    ax1 = plt.subplot(2, 1, 1)
    
    junctions = sorted(df['sensor_id'].unique())
    colors = plt.cm.Set2(range(len(junctions)))
    
    for idx, junction in enumerate(junctions):
        junction_data = hourly_traffic[hourly_traffic['sensor_id'] == junction]
        ax1.plot(junction_data['hour_of_day'], 
                junction_data['vehicle_count'], 
                marker='o', 
                linewidth=2.5, 
                markersize=8,
                label=junction.replace('_', ' '),
                color=colors[idx])
    
    ax1.set_xlabel('Time of Day (Hour)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Total Vehicle Count', fontsize=13, fontweight='bold')
    ax1.set_title('Traffic Volume vs. Time of Day (All Junctions)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(range(0, 24))
    
    # Add peak hour annotations
    for junction in junctions:
        junction_data = hourly_traffic[hourly_traffic['sensor_id'] == junction]
        if not junction_data.empty:
            peak_hour = junction_data.loc[junction_data['vehicle_count'].idxmax()]
            ax1.annotate(f'Peak: {int(peak_hour["vehicle_count"])}', 
                        xy=(peak_hour['hour_of_day'], peak_hour['vehicle_count']),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, alpha=0.7,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    # Secondary plot: Comparative Bar Chart
    ax2 = plt.subplot(2, 1, 2)
    
    # Create grouped bar chart for better comparison
    pivot_data = hourly_traffic.pivot(index='hour_of_day', columns='sensor_id', values='vehicle_count')
    pivot_data.columns = [col.replace('_', ' ') for col in pivot_data.columns]
    
    pivot_data.plot(kind='bar', ax=ax2, width=0.8, color=colors)
    ax2.set_xlabel('Time of Day (Hour)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Vehicle Count', fontsize=13, fontweight='bold')
    ax2.set_title('Hourly Traffic Distribution by Junction', fontsize=14, fontweight='bold', pad=15)
    ax2.legend(title='Junction', fontsize=10, title_fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0, ha='center')
    
    plt.tight_layout()
    
    return plt.gcf()

def generate_analytical_table():
    """Generate analytical table with peak hour analysis"""
    print("📋 Generating Analytical Table...")
    
    df = get_traffic_data()
    alerts = get_critical_alerts()
    
    if df.empty:
        return pd.DataFrame()
    
    # Calculate statistics per junction
    analysis = []
    
    for junction in sorted(df['sensor_id'].unique()):
        junction_data = df[df['sensor_id'] == junction]
        junction_alerts = alerts[alerts['sensor_id'] == junction] if not alerts.empty else pd.DataFrame()
        
        # Find peak hour
        hourly = junction_data.groupby('hour_of_day')['vehicle_count'].sum()
        peak_hour = hourly.idxmax()
        peak_vehicles = hourly.max()
        
        # Calculate average metrics
        avg_speed = junction_data['avg_speed'].mean()
        avg_congestion = junction_data['congestion_index'].mean()
        total_vehicles = junction_data['vehicle_count'].sum()
        critical_alerts = len(junction_alerts)
        
        # Determine if intervention is required
        requires_intervention = (
            avg_congestion > 5.0 or 
            critical_alerts > 10 or 
            avg_speed < 15
        )
        
        # Recommendation
        if requires_intervention:
            if critical_alerts > 30:
                recommendation = "URGENT: Deploy traffic police immediately"
            elif avg_congestion > 7.0:
                recommendation = "HIGH: Deploy traffic police during peak hours"
            else:
                recommendation = "MEDIUM: Monitor closely, consider deployment"
        else:
            recommendation = "LOW: Continue monitoring"
        
        analysis.append({
            'Junction': junction.replace('_', ' '),
            'Peak Hour': f"{int(peak_hour)}:00",
            'Peak Vehicles': int(peak_vehicles),
            'Total Vehicles': int(total_vehicles),
            'Avg Speed (km/h)': f"{avg_speed:.1f}",
            'Avg Congestion Index': f"{avg_congestion:.2f}",
            'Critical Alerts': critical_alerts,
            'Intervention Required': 'YES' if requires_intervention else 'NO',
            'Recommendation': recommendation
        })
    
    return pd.DataFrame(analysis)

def generate_complete_analytical_report(output_dir='reports'):
    """Generate complete analytical report with all deliverables"""
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("\n" + "="*70)
    print("  SMART CITY TRAFFIC ANALYTICAL REPORT GENERATOR")
    print("="*70 + "\n")
    
    # 1. MAIN REQUIREMENT: Traffic Volume vs. Time of Day (PNG)
    print("1️⃣ Generating Traffic Volume vs. Time of Day Visualization...")
    fig = generate_traffic_volume_vs_time()
    
    if fig:
        png_path = os.path.join(output_dir, f'ANALYTICAL_REPORT_Traffic_Volume_vs_Time_{timestamp}.png')
        fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   ✅ Visualization saved: {png_path}\n")
        plt.close()
    
    # 2. ANALYTICAL TABLE: Peak Hour Analysis (CSV)
    print("2️⃣ Generating Analytical Table (Peak Hour Analysis)...")
    analysis_df = generate_analytical_table()
    
    if not analysis_df.empty:
        csv_path = os.path.join(output_dir, f'ANALYTICAL_TABLE_Peak_Hour_Analysis_{timestamp}.csv')
        analysis_df.to_csv(csv_path, index=False)
        print(f"   ✅ Table saved: {csv_path}\n")
        
        # Display table in console
        print("\n" + "="*70)
        print("PEAK HOUR ANALYSIS - TRAFFIC POLICE INTERVENTION REPORT")
        print("="*70)
        print(analysis_df.to_string(index=False))
        print("="*70 + "\n")
    
    # 3. PDF REPORT: Combined Dashboard
    print("3️⃣ Generating PDF Report (Dashboard)...")
    pdf_path = os.path.join(output_dir, f'FINAL_ANALYTICAL_REPORT_{timestamp}.pdf')
    
    with PdfPages(pdf_path) as pdf:
        # Page 1: Traffic Volume vs Time
        fig1 = generate_traffic_volume_vs_time()
        if fig1:
            pdf.savefig(fig1, bbox_inches='tight')
            plt.close()
        
        # Page 2: Analytical Table as Figure
        if not analysis_df.empty:
            fig2, ax = plt.subplots(figsize=(18, 10))
            ax.axis('tight')
            ax.axis('off')
            
            # Create table with proper formatting
            table_data = analysis_df.values
            col_labels = analysis_df.columns
            
            # Adjust column widths for better fit
            col_widths = [0.13, 0.07, 0.09, 0.10, 0.09, 0.11, 0.09, 0.11, 0.21]
            
            table = ax.table(cellText=table_data, 
                           colLabels=col_labels, 
                           cellLoc='center',
                           loc='center',
                           colWidths=col_widths,
                           edges='closed')
            
            table.auto_set_font_size(False)
            table.set_fontsize(8.5)
            table.scale(1, 2.2)
            
            # Style header cells
            for i in range(len(col_labels)):
                cell = table[(0, i)]
                cell.set_facecolor('#4472C4')
                cell.set_text_props(weight='bold', color='white', ha='center', va='center')
                cell.set_height(0.08)
                cell.PAD = 0.05
            
            # Style data cells
            for i in range(1, len(table_data) + 1):
                for j in range(len(col_labels)):
                    cell = table[(i, j)]
                    cell.set_height(0.08)
                    cell.PAD = 0.05
                    
                    # Alternate row colors
                    if i % 2 == 0:
                        cell.set_facecolor('#F0F0F0')
                    else:
                        cell.set_facecolor('white')
                    
                    # Center align numeric columns
                    if j in [1, 2, 3, 4, 5, 6]:
                        cell.set_text_props(ha='center', va='center')
                    else:
                        cell.set_text_props(ha='left', va='center')
                    
                    # Highlight intervention column
                    if j == 7:  # Intervention Required column
                        if table_data[i-1][7] == 'YES':
                            cell.set_facecolor('#FFE6E6')
                            cell.set_text_props(weight='bold', color='#D00000', ha='center', va='center')
                        else:
                            cell.set_text_props(weight='bold', color='#00AA00', ha='center', va='center')
            
            plt.title('Peak Hour Analysis & Traffic Police Intervention Recommendations', 
                     fontsize=16, fontweight='bold', pad=25)
            
            pdf.savefig(fig2, bbox_inches='tight', pad_inches=0.3)
            plt.close()
        
        # Add metadata
        d = pdf.infodict()
        d['Title'] = 'Smart City Traffic Analytical Report'
        d['Author'] = 'Big Data Engineering Project'
        d['Subject'] = 'Traffic Volume vs Time of Day Analysis'
        d['Keywords'] = 'Traffic, Analytics, Peak Hours, Lambda Architecture'
        d['CreationDate'] = datetime.now()
    
    print(f"   ✅ PDF Report saved: {pdf_path}\n")
    
    # 4. SUMMARY TEXT REPORT
    print("4️⃣ Generating Summary Report...")
    summary_path = os.path.join(output_dir, f'REPORT_SUMMARY_{timestamp}.txt')
    
    df = get_traffic_data()
    alerts = get_critical_alerts()
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("     SMART CITY TRAFFIC & CONGESTION MANAGEMENT SYSTEM\n")
        f.write("              ANALYTICAL REPORT SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Period: {df['event_time'].min()} to {df['event_time'].max()}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("OVERALL STATISTICS\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Traffic Records: {len(df):,}\n")
        f.write(f"Total Critical Alerts (Speed < 10 km/h): {len(alerts):,}\n")
        f.write(f"Junctions Monitored: {df['sensor_id'].nunique()}\n")
        f.write(f"Date Range: {df['date'].nunique()} day(s)\n\n")
        
        f.write("-"*70 + "\n")
        f.write("JUNCTION-WISE ANALYSIS\n")
        f.write("-"*70 + "\n\n")
        
        for _, row in analysis_df.iterrows():
            f.write(f"📍 {row['Junction']}\n")
            f.write(f"   Peak Hour: {row['Peak Hour']} ({row['Peak Vehicles']} vehicles)\n")
            f.write(f"   Average Speed: {row['Avg Speed (km/h)']} km/h\n")
            f.write(f"   Congestion Index: {row['Avg Congestion Index']}\n")
            f.write(f"   Critical Alerts: {row['Critical Alerts']}\n")
            f.write(f"   Intervention: {row['Intervention Required']}\n")
            f.write(f"   ⚠️  {row['Recommendation']}\n\n")
        
        f.write("="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    print(f"   ✅ Summary saved: {summary_path}\n")
    
    # Final Summary
    print("\n" + "="*70)
    print("✅ ANALYTICAL REPORT GENERATION COMPLETE!")
    print("="*70)
    print("\n📦 DELIVERABLES FOR SUBMISSION:\n")
    print(f"   1. 📊 Traffic Volume vs Time (PNG): {os.path.basename(png_path)}")
    print(f"   2. 📋 Peak Hour Analysis (CSV): {os.path.basename(csv_path)}")
    print(f"   3. 📄 Complete Dashboard (PDF): {os.path.basename(pdf_path)}")
    print(f"   4. 📝 Summary Report (TXT): {os.path.basename(summary_path)}")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    generate_complete_analytical_report()
