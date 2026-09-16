"""
Quick analysis of generated data without requiring PostgreSQL.
Shows bottleneck insights, completion rates, and performance metrics.
"""

import pandas as pd
import numpy as np

def analyze_hizo():
    print("\n" + "="*70)
    print("HIZO: CROSS-BORDER PAYMENT ANALYSIS")
    print("="*70)
    
    df = pd.read_csv('data/hizo_transactions.csv')
    
    print(f"\nTotal Transactions: {len(df):,}")
    print(f"Date Range: {df['initiation_time'].min()} to {df['initiation_time'].max()}")
    
    print("\n📊 COMPLETION METRICS:")
    status_dist = df['status'].value_counts()
    total = len(df)
    for status, count in status_dist.items():
        pct = (count/total)*100
        print(f"  {status.upper():12} {count:6,} ({pct:5.1f}%)")
    
    print("\n⏱️  PROCESSING TIME ANALYSIS:")
    completed = df[df['status'] == 'completed']
    print(f"  Average Processing Time: {completed['total_duration_sec'].mean():.2f}s")
    print(f"  Median Processing Time:  {completed['total_duration_sec'].median():.2f}s")
    print(f"  P95 Processing Time:     {completed['total_duration_sec'].quantile(0.95):.2f}s")
    print(f"  P99 Processing Time:     {completed['total_duration_sec'].quantile(0.99):.2f}s")
    print(f"  Max Processing Time:     {completed['total_duration_sec'].max():.2f}s")
    
    print("\n🔗 STAGE BOTTLENECK ANALYSIS:")
    print(f"  Validation (avg):        {completed['validation_duration_sec'].mean():.2f}s")
    print(f"  Currency Conversion:     {completed['conversion_duration_sec'].mean():.2f}s")
    print(f"  Settlement (avg):        {completed['settlement_duration_sec'].mean():.2f}s")
    print(f"  Bank Latency (avg):      {completed['settlement_partner_latency_sec'].mean():.2f}s")
    
    print("\n🏦 SETTLEMENT PARTNER PERFORMANCE:")
    bank_stats = completed.groupby('settlement_partner_bank').agg({
        'settlement_partner_latency_sec': ['mean', 'max', 'count']
    }).round(2)
    bank_stats.columns = ['Avg Latency (s)', 'Max Latency (s)', 'Transactions']
    print(bank_stats.sort_values('Avg Latency (s)'))
    
    print("\n🌍 ROUTE PERFORMANCE (Top 5 by volume):")
    routes = completed.groupby(['source_country', 'destination_country']).agg({
        'total_duration_sec': ['mean', 'count']
    }).round(2).sort_values(('total_duration_sec', 'count'), ascending=False).head(5)
    routes.columns = ['Avg Duration (s)', 'Transactions']
    print(routes)

def analyze_vent():
    print("\n" + "="*70)
    print("VENT AFRICA: CRYPTO OFF-RAMP ANALYSIS")
    print("="*70)
    
    df = pd.read_csv('data/vent_africa_transactions.csv')
    
    print(f"\nTotal Transactions: {len(df):,}")
    print(f"Date Range: {df['initiation_time'].min()} to {df['initiation_time'].max()}")
    
    print("\n📊 COMPLETION METRICS:")
    status_dist = df['status'].value_counts()
    total = len(df)
    for status, count in status_dist.items():
        pct = (count/total)*100
        print(f"  {status.upper():12} {count:6,} ({pct:5.1f}%)")
    
    print("\n⏱️  PROCESSING TIME ANALYSIS:")
    completed = df[df['status'] == 'completed']
    print(f"  Average Processing Time: {completed['total_duration_sec'].mean():.2f}s")
    print(f"  Median Processing Time:  {completed['total_duration_sec'].median():.2f}s")
    print(f"  P95 Processing Time:     {completed['total_duration_sec'].quantile(0.95):.2f}s")
    print(f"  P99 Processing Time:     {completed['total_duration_sec'].quantile(0.99):.2f}s")
    print(f"  Max Processing Time:     {completed['total_duration_sec'].max():.2f}s")
    
    print("\n🔗 KYC BOTTLENECK ANALYSIS (By User Tier):")
    tier_analysis = completed.groupby('user_tier').agg({
        'kyc_verification_duration_sec': 'mean',
        'bank_processing_latency_sec': 'mean',
        'total_duration_sec': 'mean'
    }).round(2)
    tier_analysis.columns = ['Avg KYC Time (s)', 'Avg Bank Latency (s)', 'Total Time (s)']
    print(tier_analysis)
    
    print("\n💥 FAILURE ANALYSIS:")
    failed = df[df['status'] == 'failed']
    if len(failed) > 0:
        failure_dist = failed['failure_reason'].value_counts()
        for reason, count in failure_dist.items():
            pct = (count/len(failed))*100
            print(f"  {reason:20} {count:4,} ({pct:5.1f}%)")
    
    print("\n📈 CRYPTO ASSET DISTRIBUTION:")
    asset_dist = completed.groupby('crypto_asset').agg({
        'total_duration_sec': ['mean', 'count']
    }).round(2)
    asset_dist.columns = ['Avg Time (s)', 'Transactions']
    print(asset_dist)

def analyze_merchant():
    print("\n" + "="*70)
    print("MERCHANT FULFILLMENT: ORDER WORKFLOW ANALYSIS")
    print("="*70)
    
    df = pd.read_csv('data/merchant_fulfillment.csv')
    
    print(f"\nTotal Orders: {len(df):,}")
    print(f"Date Range: {df['initiation_time'].min()} to {df['initiation_time'].max()}")
    
    print("\n📊 FULFILLMENT STATUS:")
    status_dist = df['status'].value_counts()
    total = len(df)
    for status, count in status_dist.items():
        pct = (count/total)*100
        print(f"  {status.upper():12} {count:6,} ({pct:5.1f}%)")
    
    print("\n⏱️  PROCESSING TIME ANALYSIS:")
    completed = df[df['status'] == 'completed']
    print(f"  Average Processing Time: {completed['total_duration_sec'].mean():.2f}s")
    print(f"  Median Processing Time:  {completed['total_duration_sec'].median():.2f}s")
    print(f"  P95 Processing Time:     {completed['total_duration_sec'].quantile(0.95):.2f}s")
    print(f"  Max Processing Time:     {completed['total_duration_sec'].max():.2f}s")
    
    print("\n🔗 STAGE-BY-STAGE BOTTLENECK (Avg Duration):")
    stages = {
        'Validation': 'validation_duration_sec',
        'Payment Processing': 'payment_processing_duration_sec',
        'Inventory Check': 'inventory_check_duration_sec',
        'Fulfillment Assignment': 'fulfillment_assignment_duration_sec',
    }
    for stage_name, col in stages.items():
        avg_time = completed[col].mean()
        print(f"  {stage_name:25} {avg_time:6.2f}s")
    
    print("\n🏢 WAREHOUSE PERFORMANCE:")
    warehouse_stats = completed.groupby('warehouse').agg({
        'total_duration_sec': ['mean', 'count']
    }).round(2).sort_values(('total_duration_sec', 'mean'))
    warehouse_stats.columns = ['Avg Time (s)', 'Orders']
    print(warehouse_stats)
    
    print("\n💳 PAYMENT METHOD IMPACT:")
    payment_stats = completed.groupby('payment_method').agg({
        'total_duration_sec': ['mean', 'count']
    }).round(2).sort_values(('total_duration_sec', 'mean'))
    payment_stats.columns = ['Avg Time (s)', 'Orders']
    print(payment_stats)

def analyze_api():
    print("\n" + "="*70)
    print("API RESPONSE LOGS: SYSTEM PERFORMANCE")
    print("="*70)
    
    df = pd.read_csv('data/api_logs.csv')
    
    print(f"\nTotal API Requests: {len(df):,}")
    print(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    print("\n📊 HTTP STATUS DISTRIBUTION:")
    status_dist = df['status_code'].value_counts().sort_index()
    for status, count in status_dist.items():
        pct = (count/len(df))*100
        print(f"  {status}: {count:6,} ({pct:5.1f}%)")
    
    print("\n⚡ RESPONSE TIME ANALYSIS (All Requests):")
    print(f"  Average Response Time:  {df['response_time_ms'].mean():.0f}ms")
    print(f"  Median Response Time:   {df['response_time_ms'].median():.0f}ms")
    print(f"  P95 Response Time:      {df['response_time_ms'].quantile(0.95):.0f}ms")
    print(f"  P99 Response Time:      {df['response_time_ms'].quantile(0.99):.0f}ms")
    print(f"  Max Response Time:      {df['response_time_ms'].max():.0f}ms")
    
    successful = df[df['status_code'] == 200]
    print("\n✅ SUCCESSFUL REQUESTS (200 OK):")
    print(f"  Average Response Time:  {successful['response_time_ms'].mean():.0f}ms")
    print(f"  P95 Response Time:      {successful['response_time_ms'].quantile(0.95):.0f}ms")
    print(f"  P99 Response Time:      {successful['response_time_ms'].quantile(0.99):.0f}ms")
    
    print("\n🔌 ENDPOINT PERFORMANCE (P95 Response Time):")
    endpoint_stats = successful.groupby('endpoint')['response_time_ms'].agg(['mean', 'max', lambda x: x.quantile(0.95), 'count']).round(0)
    endpoint_stats.columns = ['Avg (ms)', 'Max (ms)', 'P95 (ms)', 'Requests']
    endpoint_stats = endpoint_stats.sort_values('P95 (ms)', ascending=False)
    print(endpoint_stats)
    
    print("\n🏢 COMPANY API HEALTH:")
    company_stats = df.groupby('company').agg({
        'response_time_ms': ['mean', 'max', lambda x: x.quantile(0.95)],
        'status_code': lambda x: (x == 200).sum() / len(x) * 100
    }).round(2)
    company_stats.columns = ['Avg (ms)', 'Max (ms)', 'P95 (ms)', 'Success Rate %']
    print(company_stats)

if __name__ == '__main__':
    print("\n" + "🚀 OPERATIONAL BOTTLENECK ANALYSIS" + " "*35)
    
    analyze_hizo()
    analyze_vent()
    analyze_merchant()
    analyze_api()
    
    print("\n" + "="*70)
    print("NEXT STEPS: Load data into PostgreSQL and create Power BI dashboards")
    print("="*70 + "\n")
