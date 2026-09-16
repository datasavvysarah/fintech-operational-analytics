"""
Synthetic data generator for operational turnaround & bottleneck reporting.
Generates realistic transaction and workflow logs for Hizo, Trazo, and Vent Africa.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
from faker import Faker

fake = Faker()

def generate_hizo_transactions(num_records=5000):
    """
    Generate cross-border payment transaction logs for Hizo.
    Models: currency conversion, settlement across African countries.
    """
    companies = ['Hizo', 'Hizo', 'Hizo']
    countries = ['NG', 'GH', 'KE', 'TZ', 'UG', 'RW', 'BW', 'ZA']
    currencies = ['NGN', 'GHS', 'KES', 'TZS', 'UGX', 'RWF', 'BWP', 'ZAR']

    transactions = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        transaction_id = f"HIZO-{uuid.uuid4().hex[:12].upper()}"
        company = random.choice(companies)

        initiation_time = base_time + timedelta(seconds=random.randint(0, 86400*30))

        validation_delay = random.choices(
            [random.uniform(0.5, 2), random.uniform(5, 30)],
            weights=[0.85, 0.15]
        )[0]

        conversion_delay = random.choices(
            [random.uniform(0.1, 1), random.uniform(2, 15)],
            weights=[0.90, 0.10]
        )[0]

        settlement_delay = random.choices(
            [random.uniform(1, 5), random.uniform(10, 60)],
            weights=[0.80, 0.20]
        )[0]

        status = random.choices(
            ['completed', 'failed', 'pending'],
            weights=[0.88, 0.10, 0.02]
        )[0]

        completion_time = initiation_time + timedelta(seconds=validation_delay + conversion_delay + settlement_delay)

        source_country = random.choice(countries)
        dest_country = random.choice([c for c in countries if c != source_country])

        transactions.append({
            'transaction_id': transaction_id,
            'company': company,
            'transaction_type': 'cross_border_payment',
            'initiation_time': initiation_time,
            'completion_time': completion_time,
            'status': status,
            'source_country': source_country,
            'destination_country': dest_country,
            'source_currency': source_country if source_country in currencies else 'NGN',
            'destination_currency': dest_country if dest_country in currencies else 'GHS',
            'amount_source': round(random.uniform(100, 10000), 2),
            'validation_duration_sec': validation_delay,
            'conversion_duration_sec': conversion_delay,
            'settlement_duration_sec': settlement_delay,
            'total_duration_sec': validation_delay + conversion_delay + settlement_delay,
            'settlement_partner_bank': random.choice(['CBN', 'Standard Chartered', 'Barclays', 'GTBank', 'Access Bank']),
            'settlement_partner_latency_sec': random.uniform(0.5, 30) if status == 'completed' else random.uniform(30, 120),
        })

    return pd.DataFrame(transactions)

def generate_vent_africa_transactions(num_records=3000):
    """
    Generate crypto off-ramp transaction logs for Vent Africa.
    Models: crypto to fiat conversions, settlement delays.
    """
    transactions = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        transaction_id = f"VENT-{uuid.uuid4().hex[:12].upper()}"

        initiation_time = base_time + timedelta(seconds=random.randint(0, 86400*30))

        kyc_delay = random.choices(
            [random.uniform(1, 3), random.uniform(5, 30)],
            weights=[0.92, 0.08]
        )[0]

        crypto_validation_delay = random.choices(
            [random.uniform(0.5, 2), random.uniform(3, 20)],
            weights=[0.94, 0.06]
        )[0]

        settlement_delay = random.choices(
            [random.uniform(2, 8), random.uniform(15, 90)],
            weights=[0.85, 0.15]
        )[0]

        status = random.choices(
            ['completed', 'failed', 'pending'],
            weights=[0.87, 0.11, 0.02]
        )[0]

        completion_time = initiation_time + timedelta(seconds=kyc_delay + crypto_validation_delay + settlement_delay)

        transactions.append({
            'transaction_id': transaction_id,
            'company': 'Vent Africa',
            'transaction_type': 'crypto_to_fiat_offramp',
            'initiation_time': initiation_time,
            'completion_time': completion_time,
            'status': status,
            'crypto_asset': random.choice(['USDT', 'BTC']),
            'fiat_currency': 'NGN',
            'crypto_amount': round(random.uniform(100, 100000), 8),
            'fiat_amount_expected': round(random.uniform(50000, 5000000), 2),
            'kyc_verification_duration_sec': kyc_delay,
            'crypto_validation_duration_sec': crypto_validation_delay,
            'settlement_duration_sec': settlement_delay,
            'total_duration_sec': kyc_delay + crypto_validation_delay + settlement_delay,
            'user_tier': random.choice(['tier_1', 'tier_2', 'tier_3']),
            'bank_processing_latency_sec': random.uniform(1, 45) if status == 'completed' else random.uniform(45, 180),
            'failure_reason': 'none' if status != 'failed' else random.choice(['insufficient_balance', 'kyc_failed', 'bank_timeout', 'invalid_account']),
        })

    return pd.DataFrame(transactions)

def generate_merchant_fulfillment_logs(num_records=4000):
    """
    Generate merchant order fulfillment workflow logs (for Hizo/Trazo marketplace ops).
    Models: order processing stages, inventory checks, payment processing.
    """
    transactions = []
    base_time = datetime.now() - timedelta(days=30)
    merchants = [f"Merchant_{i}" for i in range(50)]

    for i in range(num_records):
        order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        initiation_time = base_time + timedelta(seconds=random.randint(0, 86400*30))

        validation_delay = random.choices(
            [random.uniform(0.5, 1.5), random.uniform(3, 15)],
            weights=[0.88, 0.12]
        )[0]

        payment_delay = random.choices(
            [random.uniform(1, 4), random.uniform(5, 30)],
            weights=[0.82, 0.18]
        )[0]

        inventory_delay = random.choices(
            [random.uniform(0.3, 1), random.uniform(2, 20)],
            weights=[0.85, 0.15]
        )[0]

        fulfillment_delay = random.choices(
            [random.uniform(0.5, 2), random.uniform(3, 30)],
            weights=[0.90, 0.10]
        )[0]

        status = random.choices(
            ['completed', 'failed', 'processing'],
            weights=[0.86, 0.08, 0.06]
        )[0]

        completion_time = initiation_time + timedelta(
            seconds=validation_delay + payment_delay + inventory_delay + fulfillment_delay
        )

        transactions.append({
            'order_id': order_id,
            'company': random.choice(['Hizo', 'Trazo']),
            'transaction_type': 'merchant_order_fulfillment',
            'initiation_time': initiation_time,
            'completion_time': completion_time,
            'status': status,
            'merchant_id': random.choice(merchants),
            'order_amount': round(random.uniform(1000, 100000), 2),
            'validation_duration_sec': validation_delay,
            'payment_processing_duration_sec': payment_delay,
            'inventory_check_duration_sec': inventory_delay,
            'fulfillment_assignment_duration_sec': fulfillment_delay,
            'total_duration_sec': validation_delay + payment_delay + inventory_delay + fulfillment_delay,
            'items_count': random.randint(1, 20),
            'payment_method': random.choice(['mobile_money', 'bank_transfer', 'card', 'wallet']),
            'warehouse': random.choice(['Lagos', 'Accra', 'Nairobi', 'Dar es Salaam']),
            'failure_reason': 'none' if status != 'failed' else random.choice(['payment_declined', 'out_of_stock', 'address_invalid', 'system_error']),
        })

    return pd.DataFrame(transactions)

def generate_api_response_logs(num_records=6000):
    """
    Generate API response and system logs showing latencies.
    Models: third-party API calls, database queries, external service calls.
    """
    logs = []
    base_time = datetime.now() - timedelta(days=30)
    endpoints = [
        'GET /api/rates',
        'POST /api/transactions',
        'GET /api/user',
        'POST /api/settlement',
        'GET /api/balance',
        'POST /api/verify-kyc',
        'GET /api/order-status',
        'POST /api/initiate-payment',
    ]

    for i in range(num_records):
        log_id = f"LOG-{uuid.uuid4().hex[:10].upper()}"
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400*30))

        endpoint = random.choice(endpoints)

        response_time_ms = random.choices(
            [random.uniform(50, 500), random.uniform(500, 5000), random.uniform(5000, 30000)],
            weights=[0.80, 0.15, 0.05]
        )[0]

        status_code = random.choices(
            [200, 201, 400, 500, 503],
            weights=[0.90, 0.03, 0.03, 0.02, 0.02]
        )[0]

        company = random.choice(['Hizo', 'Vent Africa', 'Trazo'])

        logs.append({
            'log_id': log_id,
            'timestamp': timestamp,
            'company': company,
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'status_code': status_code,
            'request_size_bytes': random.randint(100, 5000),
            'response_size_bytes': random.randint(100, 50000),
            'external_api_latency_ms': random.choices(
                [random.uniform(10, 200), random.uniform(200, 2000)],
                weights=[0.85, 0.15]
            )[0] if status_code == 200 else random.uniform(100, 5000),
        })

    return pd.DataFrame(logs)

def generate_all_data(output_dir='.'):
    """Generate all synthetic datasets and save as CSV files."""
    print("Generating synthetic operational data...")

    print("  - Hizo cross-border transactions...")
    hizo_df = generate_hizo_transactions(5000)

    print("  - Vent Africa crypto off-ramp transactions...")
    vent_df = generate_vent_africa_transactions(3000)

    print("  - Merchant fulfillment workflows...")
    merchant_df = generate_merchant_fulfillment_logs(4000)

    print("  - API response logs...")
    api_df = generate_api_response_logs(6000)

    hizo_df.to_csv(f'{output_dir}/hizo_transactions.csv', index=False)
    vent_df.to_csv(f'{output_dir}/vent_africa_transactions.csv', index=False)
    merchant_df.to_csv(f'{output_dir}/merchant_fulfillment.csv', index=False)
    api_df.to_csv(f'{output_dir}/api_logs.csv', index=False)

    print(f"\nData generation complete!")
    print(f"  - Hizo: {len(hizo_df)} transactions")
    print(f"  - Vent Africa: {len(vent_df)} transactions")
    print(f"  - Merchant Fulfillment: {len(merchant_df)} orders")
    print(f"  - API Logs: {len(api_df)} entries")

    return {
        'hizo': hizo_df,
        'vent_africa': vent_df,
        'merchant': merchant_df,
        'api_logs': api_df,
    }

if __name__ == '__main__':
    generate_all_data()
