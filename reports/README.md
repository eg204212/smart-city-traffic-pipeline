# Reports Directory

This directory contains generated traffic analysis reports.

## Generated Files

After running the system, you'll find:

- `daily_traffic_analysis_YYYYMMDD.png` - Visualization dashboard
- `daily_traffic_report_YYYYMMDD.csv` - Intervention recommendations
- `traffic_report_*.png` - Manual report charts
- `traffic_summary_*.txt` - Statistical summaries
- `traffic_data_export_*.csv` - Raw data exports

## Generate Reports

### Automated (via Airflow)
Reports are automatically generated nightly at 11:59 PM.
Access Airflow UI at http://localhost:8085 to view DAG execution.

### Manual Generation
```bash
python reports/generate_report.py
```

## Report Contents

1. **Traffic Volume Over Time** - Hourly trends for all junctions
2. **Average Speed by Junction** - Bar chart with critical thresholds
3. **Congestion Index Distribution** - Box plots by junction
4. **Critical Alerts Count** - Alert frequency analysis
5. **Hourly Traffic Heatmap** - Junction × Hour heatmap
6. **Speed Distribution** - Histogram with critical threshold

All reports include the analyzed data required for project submission.
