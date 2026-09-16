# Operational Bottleneck Pipeline - Setup Guide

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install pandas numpy faker psycopg2-binary sqlalchemy python-dotenv
```

### Step 2: Generate Synthetic Data
```bash
python3 data_generator.py
```
This creates 18,000 realistic operational records across 4 CSV files (~3.5 MB total).

### Step 3: View Quick Analysis (No Database Required)
```bash
python3 quick_analysis.py
```
Shows:
- Completion rates and processing times for each company
- Stage-by-stage bottleneck identification
- Performance metrics by partner/warehouse/endpoint

---

## Full Pipeline Setup (PostgreSQL Required)

### Step 1: Create PostgreSQL Database
```bash
# Create database
createdb operational_analytics

# Load schema and create analytical views
psql operational_analytics < database_schema.sql
```

### Step 2: Configure Connection (Optional)
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials if needed
```

### Step 3: Run Data Ingestion
```bash
python3 data_ingestion.py
```

### Step 4: Verify Data in PostgreSQL
```bash
psql operational_analytics

# Check record counts
SELECT 'Transactions' as table_name, COUNT(*) FROM transactions
UNION ALL
SELECT 'Hizo Payments', COUNT(*) FROM hizo_cross_border_payments
UNION ALL
SELECT 'Vent Off-Ramp', COUNT(*) FROM vent_africa_crypto_offramp
UNION ALL
SELECT 'Merchant Orders', COUNT(*) FROM merchant_fulfillment
UNION ALL
SELECT 'API Logs', COUNT(*) FROM api_response_logs;

# View pre-built analytical views
SELECT * FROM v_transaction_bottlenecks;
SELECT * FROM v_company_daily_metrics;
SELECT * FROM v_api_performance;
```

---

## Connecting to Power BI / Tableau

### PostgreSQL Connection String
```
postgresql://user:password@localhost:5432/operational_analytics
```

### Key Views for Dashboards
1. **v_transaction_bottlenecks** - Main KPIs (completion rate, latency percentiles)
2. **v_company_daily_metrics** - Time-series trending
3. **v_api_performance** - API health monitoring
4. **v_hizo_settlement_analysis** - Partner bank performance ranking
5. **v_vent_africa_kyc_analysis** - KYC bottleneck by user tier

### Recommended Dashboard Sections

**Real-Time Monitoring**
- Live transaction status (% completed, failed, pending)
- Current average processing time by company
- Top 3 slowest processing stages

**Root Cause Analysis**
- Settlement partner latency ranking (Hizo)
- KYC failure rate by user tier (Vent)
- Payment method impact on order speed (Merchant)
- API endpoint P95/P99 response times

**Trend Analysis**
- 30-day completion rate trend with SMA
- Processing time percentile trend (P50/P95/P99)
- Failure rate breakdown by reason
- Daily transaction volume

---

## Quick SQL Queries for Analysis

### Find Slowest Transactions
```sql
SELECT 
 company, transaction_type, status,
 total_duration_sec, initiation_time
FROM transactions
WHERE total_duration_sec > 30
ORDER BY total_duration_sec DESC
LIMIT 20;
```

### Identify Failing Settlement Partners
```sql
SELECT 
 settlement_partner_bank,
 COUNT(*) as transactions,
 ROUND(100.0 * COUNT(CASE WHEN status='failed' THEN 1 END) / COUNT(*), 2) as failure_rate_pct
FROM hizo_cross_border_payments h
JOIN transactions t ON h.transaction_id = t.transaction_id
GROUP BY settlement_partner_bank
ORDER BY failure_rate_pct DESC;
```

### Compare Warehouse Performance
```sql
SELECT 
 warehouse,
 COUNT(*) as orders,
 ROUND(AVG(total_duration_sec), 2) as avg_processing_time_sec,
 ROUND(100.0 * COUNT(CASE WHEN status='completed' THEN 1 END) / COUNT(*), 2) as completion_rate_pct
FROM merchant_fulfillment
GROUP BY warehouse
ORDER BY avg_processing_time_sec DESC;
```

### Analyze API Dependency Impact
```sql
SELECT 
 endpoint,
 ROUND(AVG(response_time_ms), 0) as avg_response_time_ms,
 ROUND(AVG(external_api_latency_ms), 0) as avg_external_latency_ms,
 COUNT(*) as requests
FROM api_response_logs
WHERE status_code = 200
GROUP BY endpoint
ORDER BY avg_response_time_ms DESC;
```

---

## File Structure After Setup

```
/Users/sarah/Documents/Project building/
 data_generator.py # Generate synthetic data
 data_ingestion.py # Load into PostgreSQL
 quick_analysis.py # Analyze without DB
 database_schema.sql # PostgreSQL schema
 requirements.txt # Python dependencies
 .env.example # Config template
 README.md # Project overview
 SETUP.md # This file

 hizo_transactions.csv # 5,000 cross-border payments
 vent_africa_transactions.csv # 3,000 crypto off-ramps
 merchant_fulfillment.csv # 4,000 orders
 api_logs.csv # 6,000 API requests

 .claude/ # Claude Code config
```

---

## Troubleshooting

### "pip: command not found"
Use `python3 -m pip install ...` instead

### "psycopg2.OperationalError: could not connect to server"
- Ensure PostgreSQL is running: `brew services start postgresql`
- Check credentials in `.env` file
- Verify database exists: `psql -l | grep operational_analytics`

### "CSV file not found"
Run `python3 data_generator.py` first to create data files

### "ModuleNotFoundError: No module named 'pandas'"
Install missing packages: `pip install -r requirements.txt`

---

## Next Steps

1. **Data Generation** - Generate synthetic operational logs
2. **Quick Analysis** - View insights without database
3. **PostgreSQL Setup** - Load data into analytical store
4. **Power BI/Tableau** - Connect and build dashboards
5. **Alerting** - Set up real-time bottleneck detection

---

**Ready to dive in?** Start with Step 1 above or run `python3 quick_analysis.py` to see data insights immediately!
