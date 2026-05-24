CREATE DATABASE market_intelligence;

\c market_intelligence;

CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    symbol VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_metrics (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    price_usd NUMERIC(20, 8),
    market_cap NUMERIC(25, 2),
    volume_24h NUMERIC(25, 2),
    change_24h NUMERIC(10, 4),
    is_volatile BOOLEAN DEFAULT FALSE,
    fetched_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS trend_analysis (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50),
    name VARCHAR(100),
    symbol VARCHAR(20),
    market_cap_rank INTEGER,
    fetched_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS global_metrics (
    id SERIAL PRIMARY KEY,
    total_market_cap_usd NUMERIC(30, 2),
    total_volume_usd NUMERIC(30, 2),
    btc_dominance NUMERIC(8, 4),
    eth_dominance NUMERIC(8, 4),
    active_coins INTEGER,
    fetched_at TIMESTAMPTZ NOT NULL
);

-- indexes for fast time-based queries
CREATE INDEX idx_market_metrics_coin_time ON market_metrics(coin_id, fetched_at DESC);
CREATE INDEX idx_trend_time ON trend_analysis(fetched_at DESC);
