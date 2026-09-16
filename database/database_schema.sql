-- PostgreSQL Schema for Operational Turnaround & Bottleneck Reporting Pipeline

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    company VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(100) NOT NULL,
    initiation_time TIMESTAMP NOT NULL,
    completion_time TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    total_duration_sec FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hizo_cross_border_payments (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL REFERENCES transactions(transaction_id),
    source_country VARCHAR(10),
    destination_country VARCHAR(10),
    source_currency VARCHAR(10),
    destination_currency VARCHAR(10),
    amount_source DECIMAL(15,2),
    validation_duration_sec FLOAT,
    conversion_duration_sec FLOAT,
    settlement_duration_sec FLOAT,
    settlement_partner_bank VARCHAR(100),
    settlement_partner_latency_sec FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vent_africa_crypto_offramp (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL REFERENCES transactions(transaction_id),
    crypto_asset VARCHAR(20),
    fiat_currency VARCHAR(10),
    crypto_amount DECIMAL(20,8),
    fiat_amount_expected DECIMAL(15,2),
    kyc_verification_duration_sec FLOAT,
    crypto_validation_duration_sec FLOAT,
    settlement_duration_sec FLOAT,
    user_tier VARCHAR(50),
    bank_processing_latency_sec FLOAT,
    failure_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS merchant_fulfillment (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    company VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(100) NOT NULL,
    initiation_time TIMESTAMP NOT NULL,
    completion_time TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    merchant_id VARCHAR(100),
    order_amount DECIMAL(15,2),
    validation_duration_sec FLOAT,
    payment_processing_duration_sec FLOAT,
    inventory_check_duration_sec FLOAT,
    fulfillment_assignment_duration_sec FLOAT,
    total_duration_sec FLOAT,
    items_count INT,
    payment_method VARCHAR(50),
    warehouse VARCHAR(100),
    failure_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_response_logs (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    company VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    response_time_ms FLOAT,
    status_code INT,
    request_size_bytes INT,
    response_size_bytes INT,
    external_api_latency_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes (PostgreSQL syntax)
CREATE INDEX IF NOT EXISTS idx_transactions_company_date ON transactions(company, initiation_time);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);

CREATE INDEX IF NOT EXISTS idx_hizo_source_dest ON hizo_cross_border_payments(source_country, destination_country);
CREATE INDEX IF NOT EXISTS idx_hizo_bank ON hizo_cross_border_payments(settlement_partner_bank);

CREATE INDEX IF NOT EXISTS idx_vent_crypto_asset ON vent_africa_crypto_offramp(crypto_asset);
CREATE INDEX IF NOT EXISTS idx_vent_user_tier ON vent_africa_crypto_offramp(user_tier);

CREATE INDEX IF NOT EXISTS idx_merchant_company_date ON merchant_fulfillment(company, initiation_time);
CREATE INDEX IF NOT EXISTS idx_merchant_merchant ON merchant_fulfillment(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_warehouse ON merchant_fulfillment(warehouse);
CREATE INDEX IF NOT EXISTS idx_merchant_status ON merchant_fulfillment(status);

CREATE INDEX IF NOT EXISTS idx_api_company_endpoint ON api_response_logs(company, endpoint);
CREATE INDEX IF NOT EXISTS idx_api_timestamp ON api_response_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_status_code ON api_response_logs(status_code);

-- Views for Analysis

CREATE OR REPLACE VIEW v_transaction_bottlenecks AS
SELECT 
    company,
    transaction_type,
    status,
    COUNT(*) as total_transactions,
    AVG(total_duration_sec) as avg_duration_sec,
    MAX(total_duration_sec) as max_duration_sec,
    MIN(total_duration_sec) as min_duration_sec,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_duration_sec) as p95_duration_sec,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY total_duration_sec) as p99_duration_sec,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as completion_rate_pct
FROM transactions
GROUP BY company, transaction_type, status;

CREATE OR REPLACE VIEW v_company_daily_metrics AS
SELECT 
    company,
    DATE(initiation_time) as date,
    COUNT(*) as transactions_count,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as completion_rate_pct,
    AVG(total_duration_sec) as avg_duration_sec,
    MAX(total_duration_sec) as max_duration_sec
FROM transactions
GROUP BY company, DATE(initiation_time)
ORDER BY date DESC;

CREATE OR REPLACE VIEW v_api_performance AS
SELECT 
    company,
    endpoint,
    status_code,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_response_time_ms,
    MAX(response_time_ms) as max_response_time_ms,
    MIN(response_time_ms) as min_response_time_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_response_time_ms
FROM api_response_logs
GROUP BY company, endpoint, status_code;

CREATE OR REPLACE VIEW v_hizo_settlement_analysis AS
SELECT 
    settlement_partner_bank,
    COUNT(*) as transactions,
    AVG(settlement_partner_latency_sec) as avg_latency_sec,
    MAX(settlement_partner_latency_sec) as max_latency_sec,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY settlement_partner_latency_sec) as p95_latency_sec
FROM hizo_cross_border_payments
GROUP BY settlement_partner_bank;

CREATE OR REPLACE VIEW v_vent_africa_kyc_analysis AS
SELECT 
    user_tier,
    COUNT(*) as transactions,
    AVG(kyc_verification_duration_sec) as avg_kyc_duration_sec,
    AVG(bank_processing_latency_sec) as avg_bank_latency_sec,
    ROUND(100.0 * COUNT(CASE WHEN failure_reason = 'kyc_failed' THEN 1 END) / COUNT(*), 2) as kyc_failure_rate_pct
FROM vent_africa_crypto_offramp
GROUP BY user_tier;
