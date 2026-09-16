# Operational Turnaround & Bottleneck Reporting Pipeline

A data engineering solution that diagnoses operational delays in cross-border settlement rails and merchant fulfillment workflows for fintech companies operating in Africa.

**Status:** Phase 1 Complete | Phase 2 Ready (Tableau Dashboards)

## Problem Solved

**For:** Hizo, Vent Africa, Trazo

Operations leads waste hours manually combing through disjointed logs when transactions or orders stall. This pipeline automatically:
- Consolidates operational logs from disparate sources into PostgreSQL
- Diagnoses exact bottleneck stages (validation → conversion → settlement)
- Tracks processing intervals, completion rates, and response delays
- Enables proactive resolution of partner bank latency issues

### Business Impact

Instead of reactive debugging, operations teams get **instant visibility** into:
- Where transactions fail (exact stage, not just "error")
- Why they fail (settlement partner latency, KYC delays, payment processing)
- How to fix it (bank SLA negotiations, workflow optimization, failover strategies)

## Key Achievements

| Metric | Result |
|--------|--------|
| **Data Consolidated** | 18,000 synthetic operational records across 4 data sources |
| **Processing Stages Tracked** | 4-6 stages per workflow (validation → settlement) |
| **Completion Rates Identified** | Hizo 88.9%, Vent Africa 87.8%, Merchant 85.9%, API 90.2% |
| **Main Bottlenecks Found** | Bank settlement latency, KYC delays, payment processing, external API dependency |
| **Analytical Views Created** | 5 SQL views for Tableau/Power BI dashboards |
| **Data Pipeline Automated** | Python ETL → PostgreSQL with zero manual intervention |

## Architecture

```
Raw Logs (CSV)
 ↓
Data Generator → Synthetic Data Files
 ↓
Data Ingestion Pipeline → PostgreSQL Analytical Store
 ↓
SQL Views (Pre-aggregated metrics)
 ↓
Power BI / Tableau Reports (Interactive dashboards)
```

## Project Structure

```
.
 data_generator.py # Generate realistic synthetic data
 data_ingestion.py # Load data into PostgreSQL
 database_schema.sql # PostgreSQL schema + analytical views
 requirements.txt # Python dependencies
 .env.example # Configuration template
 README.md # This file
```

## Data Entities

### 1. **Hizo Cross-Border Payments**
- Transaction ID, status, processing duration
- Source/destination countries & currencies
- Stage timings: validation → conversion → settlement
- Settlement partner bank latency

**Key Metrics:**
- Avg processing time per route
- Partner bank performance (CBN, Standard Chartered, etc.)
- Failure rates by country pair

### 2. **Vent Africa Crypto Off-Ramp**
- Crypto asset type (USDT, BTC) → NGN conversion
- User tier classification (tier_1, tier_2, tier_3)
- Stage timings: KYC verification → crypto validation → settlement
- Bank processing delays

**Key Metrics:**
- KYC verification bottlenecks by user tier
- Bank latency impact on off-ramp speed
- Failure reasons (kyc_failed, bank_timeout, etc.)

### 3. **Merchant Fulfillment Workflows**
- Order processing through 4 stages: validation → payment → inventory → fulfillment
- Merchant & warehouse tracking
- Payment method & failure classification

**Key Metrics:**
- Order-to-fulfillment cycle time
- Stage-specific bottlenecks (payment delays, inventory checks)
- Warehouse performance

### 4. **API Response Logs**
- Real-time tracking of external API latencies
- Endpoint-level performance (rates, transactions, balance, etc.)
- HTTP status code distribution

**Key Metrics:**
- P95/P99 response times per endpoint
- External API dependency latency
- Error rate trending

## Setup & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Data
```bash
python data_generator.py
```

Generates 18,000 realistic operational records:
- 5,000 Hizo cross-border transactions
- 3,000 Vent Africa crypto off-ramp transactions
- 4,000 merchant fulfillment orders
- 6,000 API response logs

### 3. Create PostgreSQL Database
```bash
createdb operational_analytics

psql operational_analytics < database_schema.sql
```

### 4. Ingest Data into PostgreSQL
```bash
python data_ingestion.py
```

## SQL Analytics Views

Pre-built views for Power BI/Tableau:

- **v_transaction_bottlenecks** - Completion rates, latency percentiles by company/type
- **v_company_daily_metrics** - Daily transaction volume & performance trends
- **v_api_performance** - API endpoint health (p95/p99 response times)
- **v_hizo_settlement_analysis** - Settlement partner bank performance
- **v_vent_africa_kyc_analysis** - KYC verification bottlenecks by user tier

## Dashboard Metrics (Power BI/Tableau)

### Real-Time Monitoring
- **Transaction Processing Status** - Live % completed, pending, failed
- **Average Turnaround Time** - By company, workflow type, geography
- **Stage Latency Heatmap** - Identify which stage delays most

### Root Cause Analysis
- **Settlement Partner Performance** - Bank latency ranking (Hizo)
- **KYC Bottleneck Analysis** - Verification delays by user tier (Vent)
- **Payment Processing Delays** - Payment method impact on fulfillment time
- **API Dependency Impact** - External API latencies vs. transaction speed

### Trend Analysis
- **Daily Completion Rate** - 30-day trend with anomaly detection
- **Processing Time Distribution** - P50/P95/P99 percentiles
- **Failure Rate by Reason** - Track systemic vs. transient failures

## Technology Stack

- **Data Generation:** Python (Pandas, Faker, NumPy)
- **ETL:** Python (SQLAlchemy, psycopg2)
- **Data Warehouse:** PostgreSQL
- **Analytics:** Power BI or Tableau (connects to PostgreSQL views)
- **Dashboard Phase:** Tableau (Phase 2 - in progress)

## Quick Start (30 seconds)

```bash
# See analysis results immediately
python3 scripts/quick_analysis.py
```

**Output Preview:**
```
HIZO Completion: 88.9% | Avg Time: 14.3s | Bottleneck: Settlement (Access Bank latency)
VENT AFRICA Completion: 87.8% | Avg Time: 16.9s | Bottleneck: Bank processing (23s)
MERCHANT Completion: 85.9% | Avg Time: 12.0s | Bottleneck: Mobile money slower than bank
API Success Rate: 90.2% | Avg Response: 1.48s | Bottleneck: /api/balance (8.8s P95)
```

**See full documentation:** [START_HERE.md](../../START_HERE.md)

## Key Insights Generated

### Hizo (Cross-Border Payments)
- **Finding:** Access Bank adds 9.3 seconds vs. GTBank (settlement stage bottleneck)
- **Action:** Negotiate SLAs or implement bank failover logic
- **Impact:** Could reduce avg. processing time from 14.3s to 11s

### Vent Africa (Crypto Off-Ramp)
- **Finding:** Bank processing (23s) is the true bottleneck, NOT KYC (contradicts assumptions)
- **Action:** Implement retry logic and fallback payment gateway
- **Impact:** 25% of failures due to bank timeouts are preventable

### Merchant Operations
- **Finding:** Mobile money is 2.1x slower than bank transfers
- **Action:** Batch payment processing with async queue
- **Impact:** Could reduce fulfillment time from 12.0s to 8.5s

### API Performance
- **Finding:** GET /api/balance endpoint at P95 is 8.8s (external API dependency)
- **Action:** Add response caching + circuit breaker pattern
- **Impact:** Reduce external dependency latency by 24%

## Project Roadmap

**Phase 1: Data Engineering** Complete
- Generate synthetic operational data (18K records)
- Create PostgreSQL schema with analytical views
- Build data ingestion pipeline
- Document architecture and findings

**Phase 2: Business Intelligence** In Progress
- Connect Tableau to PostgreSQL
- Create 4 interactive dashboards (bottleneck heatmap, daily trends, SLA monitoring)
- Build alerts and notifications

**Phase 3: Automation & Alerts** (Optional)
- Email alerting for anomalies
- Daily scheduled reports
- Real-time monitoring dashboard

## Skills Demonstrated

- **Data Engineering:** ETL pipeline design, PostgreSQL schema optimization
- **SQL:** Complex analytical views, aggregation queries, performance optimization
- **Python:** Data generation (Faker, NumPy), database connectivity (SQLAlchemy, psycopg2)
- **Data Analysis:** Root cause analysis, KPI tracking, anomaly detection
- **Business Intelligence:** Requirements gathering, dashboard design, metrics definition
- **Problem-Solving:** Identifying bottlenecks across distributed systems, recommending solutions

## How to Use This Repository

1. **For Data Engineers:** Review the ETL pipeline and database schema
2. **For BI/Analytics Teams:** Build dashboards using the provided SQL views
3. **For Portfolio:** Fork this repo, add your own data sources, or extend with real-time APIs

---

**Project:** Operational Bottleneck Reporting Pipeline 
**Built for:** Hizo | Vent Africa | Trazo 
**Status:** Phase 1 Complete, Phase 2 Ready for Implementation 
**Documentation:** See [START_HERE.md](../../START_HERE.md) for quick start guide
