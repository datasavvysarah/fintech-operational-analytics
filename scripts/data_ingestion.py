"""
Data Ingestion Pipeline: Load operational logs into PostgreSQL
Reads CSV files and inserts them into the analytical store.
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class DataIngestionPipeline:
    def __init__(self, db_host=None, db_port=None, db_name=None,
                 db_user=None, db_password=None):
        db_host = db_host or os.getenv('DB_HOST', 'localhost')
        db_port = db_port or int(os.getenv('DB_PORT', 5432))
        db_name = db_name or os.getenv('DB_NAME', 'operational_analytics')
        db_user = db_user or os.getenv('DB_USER', 'postgres')
        db_password = db_password or os.getenv('DB_PASSWORD', 'postgres')
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        self.engine = None

    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_string)
            print(f"✓ Connected to PostgreSQL: {self.db_name}")
            return self.engine
        except Exception as e:
            print(f"✗ Failed to connect to PostgreSQL: {e}")
            raise

    def ingest_hizo_transactions(self, csv_file):
        """Ingest Hizo cross-border payment transactions"""
        try:
            print(f"\nIngesting Hizo transactions from {csv_file}...")
            df = pd.read_csv(csv_file)
            
            # Convert datetime columns
            df['initiation_time'] = pd.to_datetime(df['initiation_time'])
            df['completion_time'] = pd.to_datetime(df['completion_time'])
            
            # Insert into main transactions table
            trans_cols = ['transaction_id', 'company', 'transaction_type', 
                         'initiation_time', 'completion_time', 'status', 'total_duration_sec']
            df[trans_cols].to_sql('transactions', self.engine, if_exists='append', index=False)
            
            # Insert into hizo-specific table
            hizo_cols = ['transaction_id', 'source_country', 'destination_country',
                        'source_currency', 'destination_currency', 'amount_source',
                        'validation_duration_sec', 'conversion_duration_sec',
                        'settlement_duration_sec', 'settlement_partner_bank',
                        'settlement_partner_latency_sec']
            df[hizo_cols].to_sql('hizo_cross_border_payments', self.engine, 
                                if_exists='append', index=False)
            
            print(f"✓ Ingested {len(df)} Hizo transactions")
            return len(df)
        except Exception as e:
            print(f"✗ Failed to ingest Hizo transactions: {e}")
            raise

    def ingest_vent_transactions(self, csv_file):
        """Ingest Vent Africa crypto off-ramp transactions"""
        try:
            print(f"\nIngesting Vent Africa transactions from {csv_file}...")
            df = pd.read_csv(csv_file)
            
            df['initiation_time'] = pd.to_datetime(df['initiation_time'])
            df['completion_time'] = pd.to_datetime(df['completion_time'])
            
            # Insert into main transactions table
            trans_cols = ['transaction_id', 'company', 'transaction_type',
                         'initiation_time', 'completion_time', 'status', 'total_duration_sec']
            df[trans_cols].to_sql('transactions', self.engine, if_exists='append', index=False)
            
            # Insert into vent-specific table
            vent_cols = ['transaction_id', 'crypto_asset', 'fiat_currency',
                        'crypto_amount', 'fiat_amount_expected',
                        'kyc_verification_duration_sec', 'crypto_validation_duration_sec',
                        'settlement_duration_sec', 'user_tier', 'bank_processing_latency_sec',
                        'failure_reason']
            df[vent_cols].to_sql('vent_africa_crypto_offramp', self.engine,
                                if_exists='append', index=False)
            
            print(f"✓ Ingested {len(df)} Vent Africa transactions")
            return len(df)
        except Exception as e:
            print(f"✗ Failed to ingest Vent transactions: {e}")
            raise

    def ingest_merchant_fulfillment(self, csv_file):
        """Ingest merchant fulfillment orders"""
        try:
            print(f"\nIngesting Merchant fulfillment orders from {csv_file}...")
            df = pd.read_csv(csv_file)
            
            df['initiation_time'] = pd.to_datetime(df['initiation_time'])
            df['completion_time'] = pd.to_datetime(df['completion_time'])
            
            df.to_sql('merchant_fulfillment', self.engine, if_exists='append', index=False)
            
            print(f"✓ Ingested {len(df)} merchant orders")
            return len(df)
        except Exception as e:
            print(f"✗ Failed to ingest merchant fulfillment data: {e}")
            raise

    def ingest_api_logs(self, csv_file):
        """Ingest API response logs"""
        try:
            print(f"\nIngesting API logs from {csv_file}...")
            df = pd.read_csv(csv_file)
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            df.to_sql('api_response_logs', self.engine, if_exists='append', index=False)
            
            print(f"✓ Ingested {len(df)} API log entries")
            return len(df)
        except Exception as e:
            print(f"✗ Failed to ingest API logs: {e}")
            raise

    def run_pipeline(self, data_dir='.'):
        """Run the complete ingestion pipeline"""
        print("=" * 60)
        print("OPERATIONAL BOTTLENECK REPORTING PIPELINE")
        print("Data Ingestion Stage")
        print("=" * 60)

        self.connect()

        total_ingested = 0
        files = {
            'hizo_transactions.csv': self.ingest_hizo_transactions,
            'vent_africa_transactions.csv': self.ingest_vent_transactions,
            'merchant_fulfillment.csv': self.ingest_merchant_fulfillment,
            'api_logs.csv': self.ingest_api_logs,
        }

        for filename, ingest_func in files.items():
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                total_ingested += ingest_func(filepath)
            else:
                print(f"⚠ File not found: {filepath}")

        print("\n" + "=" * 60)
        print(f"PIPELINE COMPLETE: {total_ingested} records ingested")
        print("=" * 60)

if __name__ == '__main__':
    pipeline = DataIngestionPipeline()
    pipeline.run_pipeline(data_dir='data')
