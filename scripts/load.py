import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import pandas as pd
import numpy as np


def _native(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    if isinstance(v, (np.bool_,)): return bool(v)
    return v

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "market_intelligence"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def load_prices(df: pd.DataFrame):
    rows = [
        (
            r["coin_id"], _native(r["price_usd"]), _native(r["market_cap"]),
            _native(r["volume_24h"]), _native(r["change_24h"]), _native(r["is_volatile"]), r["fetched_at"]
        )
        for _, r in df.iterrows()
    ]
    sql = """
        INSERT INTO market_metrics (coin_id, price_usd, market_cap, volume_24h, change_24h, is_volatile, fetched_at)
        VALUES %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
    print(f"loaded {len(rows)} price rows")


def load_trending(df: pd.DataFrame):
    rows = [
        (r["coin_id"], r["name"], r["symbol"], _native(r["market_cap_rank"]), r["fetched_at"])
        for _, r in df.iterrows()
    ]
    sql = """
        INSERT INTO trend_analysis (coin_id, name, symbol, market_cap_rank, fetched_at)
        VALUES %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
    print(f"loaded {len(rows)} trending rows")


def load_global(df: pd.DataFrame):
    r = df.iloc[0]
    sql = """
        INSERT INTO global_metrics (total_market_cap_usd, total_volume_usd, btc_dominance, eth_dominance, active_coins, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                _native(r["total_market_cap_usd"]), _native(r["total_volume_usd"]),
                _native(r["btc_dominance"]), _native(r["eth_dominance"]),
                _native(r["active_coins"]), r["fetched_at"]
            ))
    print("loaded global metrics")


def run(transformed_data: dict):
    load_prices(transformed_data["prices"])
    load_trending(transformed_data["trending"])
    load_global(transformed_data["global"])


if __name__ == "__main__":
    print("run pipeline.py to execute the full ETL")
