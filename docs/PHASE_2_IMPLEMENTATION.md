# Phase 2: Tableau Dashboard Implementation Guide

## Phase 2 Overview

**Duration:** 5-7 hours 
**Objective:** Build 4 interactive Tableau dashboards for real-time operational monitoring 
**Audience:** Operations teams, managers, executives

---

## Pre-Implementation Checklist

- [ ] PostgreSQL database loaded with 18,000 records ( DONE)
- [ ] Tableau Desktop installed on your machine
- [ ] PostgreSQL running locally (`brew services start postgresql`)
- [ ] TABLEAU_SETUP.md guide available
- [ ] Database credentials handy (localhost:5432/operational_analytics)

---

## Implementation Timeline

```
DAY 1 (2-3 hours)
 9:00 AM - PostgreSQL Connection Setup (15 min)
 9:15 AM - Data Model & Joins (30 min)
 9:45 AM - Build Dashboard 1: Operations Center (45 min)
 10:30 AM - Build Dashboard 2: Root Cause Analysis (60 min)

DAY 2 (2-4 hours)
 2:00 PM - Build Dashboard 3: API Health (60 min)
 3:00 PM - Build Dashboard 4: Trends & SLA (60 min)
 4:00 PM - Add filters & interactions (45 min)
 4:45 PM - Testing & iteration (30-60 min)
 5:15 PM - Publish & share (15 min)
```

---

## Step-by-Step Implementation

### STEP 1: PostgreSQL Connection (15 minutes)

#### 1.1 Verify PostgreSQL is Running
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# If not running:
brew services start postgresql

# Test connection
psql -d operational_analytics -c "SELECT COUNT(*) FROM transactions;"
```
**Expected output:** Should show "18000" rows

#### 1.2 Connect from Tableau

1. Open **Tableau Desktop**
2. Click **Connect to Data**
3. Select **PostgreSQL**
4. Enter:
 - Server: `localhost`
 - Port: `5432`
 - Database: `operational_analytics`
 - Username: `postgres`
 - Password: (your PostgreSQL password)
5. Click **Sign In**

#### 1.3 Select Tables

When the "Table Selection" dialog appears, check these:
- [ ] transactions
- [ ] hizo_cross_border_payments
- [ ] vent_africa_crypto_offramp
- [ ] merchant_fulfillment
- [ ] api_response_logs
- [ ] v_transaction_bottlenecks
- [ ] v_company_daily_metrics
- [ ] v_api_performance
- [ ] v_hizo_settlement_analysis
- [ ] v_vent_africa_kyc_analysis

Click **OK**

**Verification:** You should see all tables in the left panel under "Data"

---

### STEP 2: Data Model & Calculated Fields (30 minutes)

#### 2.1 Create Calculated Fields

In Tableau, right-click on **Data** section and create these 6 calculated fields:

**Field 1: Processing Time Category**
```
IF [total_duration_sec] < 10 THEN "Fast "
ELSEIF [total_duration_sec] < 30 THEN "Normal "
ELSEIF [total_duration_sec] < 60 THEN "Slow "
ELSE "Very Slow "
END
```

**Field 2: Status Badge**
```
IF [status] = "completed" THEN " Completed"
ELSEIF [status] = "failed" THEN " Failed"
ELSE "⏳ Pending"
END
```

**Field 3: SLA Met**
```
IF [total_duration_sec] <= 60 THEN " YES" 
ELSE " NO" 
END
```

**Field 4: Processing Minutes**
```
[total_duration_sec] / 60
```

**Field 5: Date Only**
```
DATE([initiation_time])
```

**Field 6: Response Category**
```
IF [response_time_ms] < 1000 THEN "Fast "
ELSEIF [response_time_ms] < 5000 THEN "Normal "
ELSE "Slow "
END
```

**Verification:** All 6 fields should appear in blue under "Calculated Fields" in the left panel

---

### STEP 3: Dashboard 1 - Operations Center (45 minutes)

#### 3.1 Create New Sheet "Operations Center"

1. Click **New Sheet** (bottom left)
2. Rename it: Right-click → **Rename sheet** → "Operations Center"

#### 3.2 KPI Cards (Top Row)

**Create First KPI: Completion Rate %**

1. Drag **transaction_id** to **Text** (Shelf)
2. Click on **transaction_id** pill → Change to **COUNT()**
3. In Rows: Right-click → **Add Table Calculation**
 ```
 Type: Specific dimensions
 Compute: COUNTIF([status] = "completed") / COUNT([transaction_id])
 Format: Percentage
 ```
4. Format: Bold, 28pt, Green color
5. Right-click → **Edit tooltip** → Add "%"

**Create Second KPI: Avg Processing Time**
1. Drag **total_duration_sec** to **Text**
2. Change aggregation to **Average**
3. Format: Bold, 28pt, "0 sec"
4. Conditional color: Green if < 15s, Yellow if 15-30s, Red if > 30s

**Create Third KPI: P95 Latency**
1. Drag **total_duration_sec** to **Text** (create new sheet region)
2. Right-click → **Add Table Calculation** → PERCENTILE(..., 0.95)
3. Format: Bold, 28pt, "0 sec"

#### 3.3 Status Breakdown (Pie Chart)

1. Create new sheet
2. Drag **status** to **Rows**
3. Drag **transaction_id** to **Values** → COUNT()
4. Change chart type: **Pie Chart**
5. Drag **status** to **Color**
6. Colors:
 - Completed: Green (#00C465)
 - Failed: Red (#F76162)
 - Pending: Gray (#BDBDBD)
7. Add data labels: Right-click chart → **Show labels**

#### 3.4 Completion by Company (Bar Chart)

1. Create new sheet
2. Drag **company** to **Rows**
3. Drag **transaction_id** to **Values** (COUNT)
4. Create calculated field: `COUNTIF([status] = "completed") / COUNT([transaction_id])`
5. Change aggregation to **Percentage**
6. Sort: Descending
7. Colors: Use company palette

#### 3.5 Processing Time Distribution (Histogram)

1. Create new sheet
2. Drag **total_duration_sec** to **Rows**
3. Right-click → **Create Bins** → 10-second buckets
4. Drag **transaction_id** to **Values** (COUNT)
5. Change to **Area** chart
6. Add reference lines: 
 - 30s (warning) - Orange
 - 60s (critical) - Red

**Layout Tip:** Arrange the 4 charts:
```

 KPI 1 KPI 2 KPI 3 (Top row)

 Pie Chart Completion by Company (Middle)

 Processing Time Distribution (Bottom)

```

---

### STEP 4: Dashboard 2 - Root Cause Analysis (60 minutes)

#### 4.1 Stage Duration (Hizo)

1. Create new sheet: "Stage Duration"
2. Add filters:
 - Company = "Hizo"
3. Drag these to **Values**:
 - validation_duration_sec (avg)
 - conversion_duration_sec (avg)
 - settlement_duration_sec (avg)
 - settlement_partner_latency_sec (avg)
4. Drag **Measure Names** to **Rows**
5. Change to **Horizontal Bar** chart
6. Sort by value (descending)
7. Add data labels showing values

#### 4.2 Settlement Bank Performance (Hizo Specific)

1. Create table sheet: "Bank Performance"
2. Filter: Company = "Hizo"
3. Drag to columns:
 - settlement_partner_bank
 - COUNT(transaction_id)
 - AVG(settlement_partner_latency_sec)
 - MAX(settlement_partner_latency_sec)
 - PERCENTILE(settlement_partner_latency_sec, 0.95)
4. Format: Rename columns nicely
5. Sort: By Avg Latency (descending)
6. Apply heat map: Format → Conditional → Heatmap on Avg Latency
 - Red: > 16s
 - Yellow: 15-16s
 - Green: < 15s

#### 4.3 KYC Bottleneck (Vent Africa)

1. Create table: "KYC Analysis"
2. Filter: Company = "Vent Africa"
3. Use **v_vent_africa_kyc_analysis** view
4. Columns:
 - user_tier
 - AVG(kyc_verification_duration_sec)
 - AVG(bank_processing_latency_sec)
 - AVG(total_duration_sec)
5. Add annotation: " Bank processing (23s) is bottleneck, not KYC (3s)"

#### 4.4 Warehouse Performance (Merchant)

1. Create bar chart: "Warehouse Performance"
2. Filter: Company = "Hizo" OR "Trazo"
3. Drag **warehouse** to **Rows**
4. Drag **total_duration_sec** to **Values** (AVG)
5. Sort: Descending
6. Colors: Performance-based
7. Data labels: Show times
8. Add annotation: "Lagos leads - share practices"

#### 4.5 Payment Method Impact (Merchant)

1. Create bar chart: "Payment Methods"
2. Filter: Company = "Hizo" OR "Trazo"
3. Drag **payment_method** to **Rows**
4. Drag **total_duration_sec** to **Values** (AVG)
5. Sort: Descending
6. Highlight mobile_money in red

**Dashboard 2 Layout:**
```

 Stage Duration Bank Performance 

 KYC Bottleneck Warehouse Perf 

 Payment Method Impact 

```

---

### STEP 5: Dashboard 3 - API Health (60 minutes)

#### 5.1 API Success Metrics (KPI Cards)

Create 3 cards (similar to Dashboard 1):

**Card 1: Success Rate**
```
COUNTIF([status_code] = 200) / COUNT([log_id])
Format: Percentage
Color: Green if > 95%, Yellow if 90-95%, Red < 90%
```

**Card 2: P95 Response Time**
```
PERCENTILE([response_time_ms], 0.95)
Format: "0 ms"
Color: Green if < 5000ms, Yellow if 5-10s, Red if > 10s
```

**Card 3: Total Requests**
```
COUNT([log_id])
Format: "0 requests"
```

#### 5.2 Response Time by Endpoint (Bar Chart)

1. Drag **endpoint** to **Rows**
2. Drag **response_time_ms** to **Values** (use PERCENTILE 0.95)
3. Sort: Descending (slowest first)
4. Colors: Performance gradient
 - Red: > 8000ms
 - Yellow: 5000-8000ms
 - Green: < 5000ms
5. Data labels: Show times

#### 5.3 HTTP Status Distribution (Pie)

1. Drag **status_code** to **Rows**
2. Drag **log_id** to **Values** (COUNT)
3. Change to **Pie Chart**
4. Colors:
 - 200: Green
 - 201: Light green
 - 400/500/503: Red shades

#### 5.4 Response Time Trend (Line Chart)

1. Drag **timestamp** to **Columns** (continuous date)
2. Drag **response_time_ms** to **Values**
3. Create calculated field: 
 ```
 P95_PERCENTILE = PERCENTILE([response_time_ms], 0.95)
 ```
4. Change chart to **Line**
5. Add trend line: Analytics → Trend Line
6. Add reference line: 5000ms (SLA target) in red

#### 5.5 Company Comparison (Card View)

1. Drag **company** to **Rows**
2. Add columns:
 - Success Rate %
 - Avg Response (ms)
 - P95 Response (ms)
3. Format as table
4. Conditional formatting: Red if success < 90%

**Dashboard 3 Layout:**
```

 Success % P95 Response Total Requests

 Response Time by Endpoint 

 Status Distrib Response Time Trend 

 Company Comparison 

```

---

### STEP 6: Dashboard 4 - Trends & SLA (60 minutes)

#### 6.1 Daily Completion Rate (Area Chart)

1. Drag **initiation_time** to **Columns** (continuous date)
2. Drag **transaction_id** to **Values** (COUNT)
3. Create calculated field:
 ```
 Daily_Completion = COUNTIF([status] = "completed") / COUNT([transaction_id])
 ```
4. Change to **Area** chart
5. Add trend line: Linear
6. Add reference line: 90% (SLA target)
7. Annotation: " Anomaly detected Sept 10-12"

#### 6.2 Latency Percentiles (Multi-line)

1. Drag **initiation_time** to **Columns**
2. Drag **total_duration_sec** to **Values**
3. Create 3 calculated fields:
 ```
 P50 = PERCENTILE([total_duration_sec], 0.50)
 P95 = PERCENTILE([total_duration_sec], 0.95)
 P99 = PERCENTILE([total_duration_sec], 0.99)
 ```
4. Change to **Line** chart
5. Use different colors: P50=green, P95=orange, P99=red
6. Add reference lines: 30s, 60s

#### 6.3 Failure Reason Breakdown (Stacked Bar)

1. Drag **initiation_time** to **Columns** (date)
2. Drag **failure_reason** to **Rows**
3. Drag **transaction_id** to **Values** (COUNT) [filter: status = "failed"]
4. Change to **Stacked Bar**
5. Colors:
 - bank_timeout: Red
 - kyc_failed: Orange
 - insufficient_balance: Yellow
 - invalid_account: Gray

#### 6.4 Change Indicators (KPI Cards)

Create 3 comparison cards:

**Card 1: Completion Rate Change**
```
Current: [Current Completion %]
Previous Week: CALCULATE previous week average
Display: +2.5% ↑ (green) or -1.2% ↓ (red)
```

**Card 2: P95 Change**
```
Display: -5.3s ↓ (green = improvement)
```

**Card 3: Failure Rate Change**
```
Display: +0.8% ↑ (red = worse)
```

#### 6.5 Daily Volume Trending (Area Stacked)

1. Drag **initiation_time** to **Columns**
2. Drag **company** to **Rows**
3. Drag **transaction_id** to **Values** (COUNT)
4. Change to **Stacked Area**
5. Add label: Total volume above chart

**Dashboard 4 Layout:**
```

 Change: % Change: P95 Change: Fail 

 Daily Completion Rate (30 days) 

 Latency Percentiles Failure Reasons 

 Daily Volume by Company 

```

---

## STEP 7: Create Master Dashboard (30 minutes)

#### 7.1 Assemble All Sheets

1. Click **New Dashboard**
2. Set size: **Laptop (1920x1080)**
3. Name it: **"Operational Analytics - Master"**

#### 7.2 Add Sheets as Tabs

1. Drag sheets from left panel to dashboard:
 - Sheet 1: Operations Center
 - Sheet 2: Root Cause Analysis
 - Sheet 3: API Health
 - Sheet 4: Trends & SLA

2. Right-click each → **Edit Tab Name** to use friendly names

#### 7.3 Add Dashboard Filters

1. Click **Filters** button
2. Add "Company" filter (applies to all sheets)
3. Add "Date Range" filter (relative dates)
4. Set defaults: Company = "All", Date = "Last 30 days"

**Verification:** Changing company filter should update all 4 tabs

---

## STEP 8: Testing & Validation (30 minutes)

### Test Checklist

- [ ] All KPI cards display numbers (no errors)
- [ ] Completion Rate is ~88.9% (Hizo) / ~87.8% (Vent) / ~85.9% (Merchant)
- [ ] Avg time is ~14.3s (Hizo) / ~16.9s (Vent) / ~12s (Merchant)
- [ ] P95 latency values match expectations
- [ ] Company filter works on all dashboards
- [ ] Date filter reduces data correctly
- [ ] Colors render properly (no black text on dark background)
- [ ] All charts have proper tooltips
- [ ] No SQL errors in status bar
- [ ] Performance is acceptable (< 5 second load times)

### Performance Optimization (if needed)

If dashboard loads slowly:

1. **Use Extract instead of Live**
 - Data Source → Right-click → "Extract Data"
 - Refresh: Daily at 6 AM

2. **Reduce visible data**
 - Add automatic "Last 30 days" filter
 - Remove unused tables from data source

3. **Simplify calculations**
 - Use table calculations sparingly
 - Pre-aggregate in PostgreSQL views (already done!)

---

## STEP 9: Export & Publishing (15 minutes)

### Option A: Save Locally

```
File → Save As
Filename: "Operational_Analytics_Phase2.twbx"
Location: /Users/sarah/Documents/Project\ building/
```

### Option B: Publish to Tableau Server (if available)

```
Server → Publish Workbook
Project: Create "Operational Analytics"
Name: "Operational Bottleneck Dashboard"
Permissions:
 - Operations team: View & Filter
 - Managers: Edit
 - Executives: View only
```

### Option C: Share via Tableau Public (Free, Cloud)

```
File → Publish to Tableau Public
(Data will be public - use only for demo purposes)
```

---

## Deliverables Checklist

- [ ] Dashboard 1: Operations Center ( Completion rate, avg time, P95, status breakdown)
- [ ] Dashboard 2: Root Cause Analysis ( Bank perf, KYC, warehouse, payment method)
- [ ] Dashboard 3: API Health ( Success rate, P95 response, endpoint perf, trends)
- [ ] Dashboard 4: Trends & SLA ( 30-day completion trend, failure reasons, anomalies)
- [ ] Dashboard filters (Company, Date Range) working
- [ ] All charts rendering without errors
- [ ] Colors matched to company brand
- [ ] Tooltips providing clear context
- [ ] Workbook saved/published

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Could not find the database" | Verify PostgreSQL running: `brew services start postgresql` |
| Blank dashboards | Check filter context - remove conflicting filters |
| Wrong numbers | Verify joins are working - check data source tabs |
| Slow performance | Use data extracts instead of live connection |
| Missing columns | Ensure all tables selected in connection dialog |
| "Cannot aggregate measure" | Dimension in wrong shelf - drag to Rows/Columns instead |

---

## Next: Phase 3 (Optional)

Once dashboards are working, Phase 3 adds:
- Real-time alerts (email when P95 > 60s)
- Scheduled reports (daily PDF to operations team)
- Anomaly detection (flag unusual patterns)
- Mobile-friendly layout

---

## Success Metrics

After Phase 2, you should be able to:

 View live transaction completion rate (88.9%) 
 Identify which settlement bank is slowest (Access Bank: 15.64s) 
 See KYC is not the bottleneck for Vent (Bank latency is!) 
 Spot warehouse performance gaps (Lagos vs Nairobi) 
 Monitor API health by endpoint 
 Detect 30-day trends and anomalies 
 Share insights with operations team via Tableau 

---

## Estimated Time Breakdown

```
PostgreSQL Connection: 15 min 
Data Model & Formulas: 30 min
Dashboard 1 (Operations): 45 min
Dashboard 2 (Root Cause): 60 min
Dashboard 3 (API Health): 60 min
Dashboard 4 (Trends): 60 min
Master Dashboard & Filters: 30 min
Testing & Optimization: 30 min
Export & Publishing: 15 min

TOTAL: 5-7 hours
```

**Realistic Timeline:** Saturday morning 9 AM → Saturday evening 5 PM 
(With breaks and iteration)

---

**Next Step:** Open Tableau and start with Step 1 above! 

See TABLEAU_SETUP.md for detailed configuration guide.
