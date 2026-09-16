# Tableau Setup Guide - Operational Bottleneck Dashboard

## Overview

This guide walks you through connecting PostgreSQL to Tableau and building 4 interactive dashboards to monitor operational bottlenecks for Hizo, Vent Africa, and Trazo.

---

## Step 1: Connect PostgreSQL to Tableau

### 1a. Start Tableau & Create New Data Source

1. Open **Tableau Desktop**
2. Click **Connect to Data** (or File → New Data Source)
3. Select **PostgreSQL**

### 1b. Enter Connection Details

```
Server: localhost
Port: 5432
Database: operational_analytics
Username: postgres
Password: [your password]
```

Click **Sign In**

### 1c. Select Tables to Import

Select all 10 tables:
- transactions
- hizo_cross_border_payments
- vent_africa_crypto_offramp
- merchant_fulfillment
- api_response_logs
- v_transaction_bottlenecks (view)
- v_company_daily_metrics (view)
- v_api_performance (view)
- v_hizo_settlement_analysis (view)
- v_vent_africa_kyc_analysis (view)

---

## Step 2: Set Up Data Model & Relationships

### Create Table Joins in Tableau

1. Click **Sheets** tab (after data source loads)
2. Drag **transactions** to canvas
3. Add relationships:

**Join 1: Hizo Payments**
```
transactions (INNER)
 transaction_id = hizo_cross_border_payments.transaction_id
hizo_cross_border_payments
```

**Join 2: Vent Off-Ramp**
```
transactions (INNER)
 transaction_id = vent_africa_crypto_offramp.transaction_id
vent_africa_crypto_offramp
```

**Join 3: API Logs**
```
transactions (LEFT OUTER)
 company = api_response_logs.company
api_response_logs
```

### Create Calculated Fields

In **Tableau Desktop**, right-click in the data pane and create:

```tableau
Processing Time (Minutes) = [total_duration_sec] / 60

Processing Time Category = 
IF [total_duration_sec] < 10 THEN "Fast "
ELSEIF [total_duration_sec] < 30 THEN "Normal "
ELSEIF [total_duration_sec] < 60 THEN "Slow "
ELSE "Very Slow "
END

Date (Extract) = DATE([initiation_time])

Month = DATEMONTH([initiation_time])

Hour = DATEPART('hour', [initiation_time])

SLA Met (P95 < 60s) = 
IF [total_duration_sec] <= 60 THEN " YES" ELSE " NO" END

Status Badge = 
IF [status] = "completed" THEN ""
ELSEIF [status] = "failed" THEN ""
ELSE "⏳"
END
```

---

## Step 3: Build Dashboard Pages

### Dashboard 1: Real-Time Operations Center

**Purpose:** Live monitoring of transaction health 
**Audience:** Operations Manager, Duty Officer

**Components:**

#### 1. KPI Summary (Top Row)
Create 3 **Single Value** cards:

**Card 1: Completion Rate %**
```
Measure: COUNT(transaction_id) [filtered: status = "completed"] / COUNT(transaction_id)
Format: Percentage (1 decimal)
Color: Green (#00C465) if > 90%, Yellow if 85-90%, Red if < 85%
Font: Bold, 28pt
```

**Card 2: Avg Processing Time**
```
Measure: AVG(total_duration_sec)
Format: 0 decimal places, append " sec"
Color: Green if < 15s, Yellow if 15-30s, Red if > 30s
Font: Bold, 28pt
```

**Card 3: P95 Latency**
```
Measure: PERCENTILE(total_duration_sec, 0.95)
Format: 0 decimal places, append " sec"
Color: Green if < 30s, Yellow if 30-60s, Red if > 60s
Font: Bold, 28pt
```

#### 2. Status Breakdown (Pie Chart)
```
Dimensions: status
Measures: COUNT(transaction_id)
Colors: 
 - Completed: Green (#00C465)
 - Failed: Red (#F76162)
 - Pending: Gray (#BDBDBD)
Tooltip: Show %
```

#### 3. Completion Rate by Company (Bar Chart)
```
Dimensions: company
Measures: COUNTIF(status = "completed") / COUNT(transaction_id)
Sort: Descending
Colors: Company palette (blue, orange, green)
Data Label: Percentage
```

#### 4. Processing Time Distribution (Histogram)
```
Dimensions: Processing Time Category (bin)
Measures: COUNT(transaction_id)
X-Axis: total_duration_sec (bins of 15 sec)
Y-Axis: Count
Color: Single color (blue)
Show: Distribution density curve overlay
```

**Filters (Left Panel):**
- Company (multi-select)
- Date Range (relative: Last 7 days, Last 30 days, etc.)
- Status (checkbox)

**Auto-Refresh:** Every 15 minutes

---

### Dashboard 2: Root Cause Analysis

**Purpose:** Identify bottleneck stages and performance gaps 
**Audience:** Operations Lead, Data Analyst

**Components:**

#### 1. Stage Duration Breakdown (Hizo) - Horizontal Bar
```
Dimensions: Custom dimension for stage types
Measures: 
 - validation_duration_sec
 - conversion_duration_sec
 - settlement_duration_sec
 - settlement_partner_latency_sec
Display: Stacked horizontal bar
Colors: Different color per stage
Sort: By total duration descending
Data Label: Show values
```

#### 2. Settlement Bank Performance (Hizo) - Ranking Table
```
Dimensions: settlement_partner_bank
Measures:
 - COUNT(transaction_id) [as "Transactions"]
 - AVG(settlement_partner_latency_sec) [as "Avg Latency"]
 - MAX(settlement_partner_latency_sec) [as "Max Latency"]
 - PERCENTILE(settlement_partner_latency_sec, 0.95) [as "P95"]
Sort: By Avg Latency descending
Heat Map: Conditional formatting on Avg Latency
 - Red: > 16s
 - Yellow: 15-16s
 - Green: < 15s
```

#### 3. KYC Bottleneck (Vent Africa) - Table
```
Dimensions: user_tier
Measures:
 - AVG(kyc_verification_duration_sec)
 - AVG(bank_processing_latency_sec)
 - AVG(total_duration_sec)
 - COUNT(transaction_id)
Insight: Highlight that bank latency >> KYC time
Annotation: " Bank processing is the bottleneck!"
```

#### 4. Warehouse Performance (Merchant) - Bar Chart
```
Dimensions: warehouse
Measures: AVG(total_duration_sec)
Sort: Descending
Color: Performance-based
 - Red: > 12s
 - Yellow: 11.5-12s
 - Green: < 11.5s
Data Label: Show time
Annotation: "Lagos is fastest - share best practices"
```

#### 5. Payment Method Impact (Merchant) - Bar Chart
```
Dimensions: payment_method
Measures: AVG(total_duration_sec)
Sort: Descending
Color: Single color (orange)
Data Label: Show time
```

**Filters:**
- Company (Hizo shows settlement partner table, Vent shows KYC table, etc.)
- Date Range

**Key Insight Box:**
```
Dynamic text showing:
"[Bank Name] is slowest at [XX.Xs latency]"
"Mobile money adds [X.Xs] vs bank transfer"
"[Warehouse] lags [Xs] behind fastest"
```

---

### Dashboard 3: API Health & System Performance

**Purpose:** Monitor external dependencies and system reliability 
**Audience:** DevOps, Platform Engineer

**Components:**

#### 1. API Success Metrics (Top Row - 3 Cards)
```
Card 1: Success Rate %
 = COUNTIF(status_code = 200) / COUNT(log_id)
 Color: Green if > 95%, Yellow if 90-95%, Red if < 90%

Card 2: P95 Response Time
 = PERCENTILE(response_time_ms, 0.95)
 Format: "4,965 ms"
 Color: Green if < 5s, Yellow if 5-10s, Red if > 10s

Card 3: Request Volume
 = COUNT(log_id)
 Format: "6,000 requests"
```

#### 2. Response Time by Endpoint (Bar Chart)
```
Dimensions: endpoint
Measures: PERCENTILE(response_time_ms, 0.95)
Sort: Descending
Color: Performance-based gradient
 - Red: > 8s
 - Yellow: 5-8s
 - Green: < 5s
Data Label: Show P95 time
Annotation: "GET /api/balance is slowest"
```

#### 3. HTTP Status Distribution (Pie Chart)
```
Dimensions: status_code
Measures: COUNT(log_id)
Colors:
 - 200: Green
 - 201: Light Green
 - 400/500/503: Red shades
Tooltip: Show count and %
```

#### 4. Response Time Trend (Line Chart - 30 days)
```
Dimensions: DATE(timestamp)
Measures: PERCENTILE(response_time_ms, 0.95)
Trend Line: Linear
Color: Blue
Reference Line: SLA target (5000 ms = red line)
Show: P50, P95, P99 as different line styles
Annotation: Highlight any spikes
```

#### 5. Company Comparison (Multi-row Card)
```
Dimensions: company
Measures:
 - Success Rate %
 - Avg Response Time (ms)
 - P95 Response Time (ms)
Format: Card view with metrics
Sort: By Success Rate descending
```

**Filters:**
- Date Range
- Endpoint (multi-select)
- Status Code (multi-select)

**Alerts/Rules:**
- Conditional formatting: Red if success < 90%
- Conditional formatting: Red if P95 > 5000ms

---

### Dashboard 4: Trend Analysis & SLA Monitoring

**Purpose:** 30-day trends and anomaly detection 
**Audience:** Operations Director, Executive

**Components:**

#### 1. Daily Completion Rate (Area Chart - 30 days)
```
Dimensions: DATE(initiation_time)
Measures: 
 - COUNTIF(status = "completed") / COUNT(transaction_id) [as Daily Rate]
 - Add Trend Line
 - Add Reference Line at 90% (SLA target)
Color:
 - Area: Light blue
 - Trend: Dark blue
 - Reference: Red dashed
Annotation: Highlight anomalies (drop below 85%)
```

#### 2. Latency Percentiles Over Time (Multi-line Chart)
```
Dimensions: DATE(initiation_time)
Measures:
 - PERCENTILE(total_duration_sec, 0.50) [P50] - Green line
 - PERCENTILE(total_duration_sec, 0.95) [P95] - Orange line
 - PERCENTILE(total_duration_sec, 0.99) [P99] - Red line
Reference Lines:
 - 30s (warning level)
 - 60s (critical level)
```

#### 3. Failure Reason Breakdown (Stacked Bar - 30 days)
```
Dimensions: DATE(initiation_time), failure_reason
Measures: COUNT(transaction_id) [filtered: status = "failed"]
Stack: failure_reason
Colors:
 - bank_timeout: Red
 - kyc_failed: Orange
 - insufficient_balance: Yellow
 - invalid_account: Gray
Tooltip: Show count and % of total failures
```

#### 4. Change Indicators (KPI Cards)
```
Card 1: Completion Rate vs Last Week
 Format: +2.5% (green up arrow) or -1.2% (red down arrow)
 Color: Green if positive, Red if negative

Card 2: P95 Latency vs Last Week
 Format: -5.3s (green down arrow = improvement)
 
Card 3: Failure Rate vs Last Week
 Format: +0.8% (red up arrow = worse)
```

#### 5. Daily Volume Trending (Area Chart)
```
Dimensions: DATE(initiation_time), company
Measures: COUNT(transaction_id)
Stack: By company
Colors: Company palette
Show: Total above chart
Tooltip: Company + count
```

**Filters:**
- Company (multi-select)
- Date Range (default: Last 30 days)

**Summary Text Box:**
```
"[Company] completed [completion_rate]% of transactions
Average processing time: [avg_time]s
P95 latency: [p95_time]s
Failures: [failure_count] ([failure_rate]%)

Key Finding: [Dynamic based on data]
- If bank_timeout > 25%: "Bank timeouts spiked!"
- If P95 > 60s: "Latency above SLA"
- If completion < 85%: " Completion rate below target"
```

---

## Step 4: Create Interactive Dashboard

### Dashboard Assembly

1. Create new **Dashboard** (File → New Dashboard)
2. Set size: **Laptop (1920x1080)** for best viewing
3. Add each sheet as a tab:
 - Tab 1: Operations Center
 - Tab 2: Root Cause Analysis
 - Tab 3: API Health
 - Tab 4: Trends & SLA

### Add Dashboard-Level Filters

```
Filters → Add Filter → Company (dropdown)
Apply to all sheets

Filters → Add Filter → Date Range (relative date)
Default: Last 30 days
Apply to all sheets
```

### Create Filter Interactions

1. Select **Company filter**
2. Right-click → **Add filter interaction**
3. Set: When **Company** changes → **Update** these sheets:
 - All sheets (filtering behavior)

---

## Step 5: Create a Drill-Down Path

### From Dashboard → Detail View

**In Tableau, add interactivity:**

1. **Operations Dashboard** → Click on a company/warehouse
2. Drill to **Root Cause dashboard** filtered to that company
3. From Root Cause → Click on a bank
4. Drill to **detailed transaction table** for that bank

**Implementation:**
```
1. Create Action: Dashboard → Operational Details
 Trigger: Click on "completion_rate" card
 Target: Filter "Root Cause Analysis" sheet by company
 
2. Create Action: Root Cause → Transactions
 Trigger: Click on "settlement_partner_bank"
 Target: Show detail view filtered by bank
```

---

## Step 6: Export & Publish

### Option 1: Save Locally
```
File → Save As → "Operational_Analytics.twbx"
```
(TWBX = packaged workbook with data)

### Option 2: Publish to Tableau Server/Cloud

```
Server → Publish Workbook
Project: "Operational Analytics"
Name: "Operational Bottleneck Dashboard"
```

**Permissions:**
- Operations team: View & filter
- Managers: Edit dashboards
- Executives: View-only

---

## Step 7: Set Up Auto-Refresh

### In Tableau Prep (Data Extract Refresh)

1. File → Extract Data
2. Right-click data source → **Extract Data**
3. Schedule refresh:
 - **Frequency:** Daily
 - **Time:** 6:00 AM UTC
 - Run during low-traffic hours

---

## Step 8: Create Alerts

### Tableau Alert Rules

In **Tableau Server/Cloud**:

1. Click on **Alerts** icon
2. Create Alert 1:
 ```
 Metric: [Completion Rate %]
 Condition: Falls below 85%
 Frequency: Daily at 9 AM
 Recipients: ops-team@hizo.com
 ```

3. Create Alert 2:
 ```
 Metric: [P95 Latency]
 Condition: Exceeds 60 seconds
 Frequency: Every 30 minutes
 Recipients: ops-oncall@hizo.com
 ```

4. Create Alert 3:
 ```
 Metric: [Bank Timeout %]
 Condition: Rises above 25%
 Frequency: Daily
 Recipients: ops-director@hizo.com
 ```

---

## Tableau Expressions Quick Reference

### Aggregate Functions
```tableau
COUNTIF([status] = "completed") // Count specific status
AVG(IF [status] = "completed" THEN [total_duration_sec] END) // Conditional average
PERCENTILE(ATTR(total_duration_sec), 0.95) // P95 percentile
WINDOW_AVG([total_duration_sec]) // Moving average (window function)
```

### Date Functions
```tableau
DATE([initiation_time]) // Extract date
DATEMONTH([initiation_time]) // Month number
DATEPART('hour', [initiation_time]) // Hour of day
DATEDIFF('day', TODAY(), [initiation_time]) // Days ago
```

### Conditional Logic
```tableau
IF [status] = "completed" THEN ""
ELSEIF [status] = "failed" THEN ""
ELSE "⏳"
END

CASE [company]
 WHEN "Hizo" THEN ""
 WHEN "Vent Africa" THEN ""
 WHEN "Trazo" THEN ""
END
```

### String Functions
```tableau
[company] + ": " + STR([completion_rate]) + "%" // Concatenate
FIND("bank", [failure_reason]) > 0 // Contains check
```

---

## Customization Tips

### Color Palette
```
Hizo (Blue): #1F77B4
Vent (Orange): #FF7F0E
Trazo (Green): #2CA02C
Completed (Green):#00C465
Failed (Red): #F76162
Pending (Gray): #BDBDBD
```

### Font Sizes
- KPI Cards: 28pt bold
- Sheet titles: 18pt bold
- Axis labels: 12pt
- Tooltips: 10pt

### Best Practices
- Use color meaningfully (red = bad, green = good)
- Add data labels to bars/cards
- Include trend indicators (↑/↓)
- Use reference lines for targets/thresholds
- Annotate key insights with text boxes

---

## Performance Optimization

### If Dashboard is Slow

1. **Use Data Extracts** instead of live connection
 - File → Data Source → Extract Data
 - Schedule refresh daily

2. **Reduce dimensions** in views (remove unnecessary detail)

3. **Use filters** to limit data shown
 - Add "Last 30 days" filter
 - Reduce transaction table rows

4. **Aggregate at source** (use PostgreSQL views)
 - Already done! v_transaction_bottlenecks pre-aggregates

5. **Simplify calculations**
 - Use window functions instead of table calculations

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection failed" | Check PostgreSQL is running: `brew services start postgresql` |
| Blank sheets | Check filter context, verify all tables connected |
| Slow refresh | Use data extracts, reduce row count with filters |
| Missing data | Verify joins are correct, check NULL values |
| Formatting issues | Use keyboard shortcut Ctrl+Z to reset, rebuild from scratch |

---

## Training & Support

### For Operations Team
- Quick reference: How to use filters, drill-down
- Tooltip interpretation
- Alert acknowledgment process

### For Analysts
- How to edit calculated fields
- Creating new worksheets
- Publishing updated dashboards

---

## Next Steps

1. Create PostgreSQL connection in Tableau
2. Build 4 dashboard pages
3. Test filters and interactions
4. Publish to Tableau Server/Cloud
5. Share with operations team
6. Configure alerts
7. Gather feedback & iterate
8. Set up scheduled extracts

**Estimated Time:** 5-7 hours for complete dashboard build

---

## Resources

- Tableau Help: https://help.tableau.com
- Tableau Community Forums: https://community.tableau.com
- Your PostgreSQL Connection: localhost:5432/operational_analytics
- Dashboard Schedule: Daily refresh at 6 AM
