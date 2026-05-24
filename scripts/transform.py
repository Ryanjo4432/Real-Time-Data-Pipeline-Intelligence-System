import pandas as pd
import os
from datetime import datetime

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def transform_prices(raw_prices: dict, batch_ts: datetime = None) -> pd.DataFrame:
    ts = batch_ts or datetime.utcnow()
    rows = []
    for coin_id, metrics in raw_prices.items():
        rows.append({
            "coin_id": coin_id,
            "price_usd": metrics.get("usd"),
            "market_cap": metrics.get("usd_market_cap"),
            "volume_24h": metrics.get("usd_24h_vol"),
            "change_24h": metrics.get("usd_24h_change"),
            "fetched_at": ts,
        })
    df = pd.DataFrame(rows)
    df.dropna(subset=["price_usd"], inplace=True)
    df["change_24h"] = df["change_24h"].round(4)
    return df


def transform_trending(raw_trending: dict, batch_ts: datetime = None) -> pd.DataFrame:
    ts = batch_ts or datetime.utcnow()
    coins = raw_trending.get("coins", [])
    rows = []
    for item in coins:
        c = item.get("item", {})
        rows.append({
            "coin_id": c.get("id"),
            "name": c.get("name"),
            "symbol": c.get("symbol"),
            "market_cap_rank": c.get("market_cap_rank"),
            "fetched_at": ts,
        })
    return pd.DataFrame(rows)


def transform_global(raw_global: dict, batch_ts: datetime = None) -> pd.DataFrame:
    ts = batch_ts or datetime.utcnow()
    data = raw_global.get("data", {})
    row = {
        "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
        "total_volume_usd": data.get("total_volume", {}).get("usd"),
        "btc_dominance": data.get("market_cap_percentage", {}).get("btc"),
        "eth_dominance": data.get("market_cap_percentage", {}).get("eth"),
        "active_coins": data.get("active_cryptocurrencies"),
        "fetched_at": ts,
    }
    return pd.DataFrame([row])


def add_volatility_flag(df: pd.DataFrame, threshold=5.0) -> pd.DataFrame:
    df["is_volatile"] = df["change_24h"].abs() > threshold
    return df


def save_processed(df: pd.DataFrame, name: str):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(PROCESSED_DIR, f"{name}_{ts}.csv")
    df.to_csv(path, index=False)
    print(f"saved -> {path}")


def run(raw_data: dict):
    batch_ts = datetime.utcnow()  # one timestamp for the whole batch
    prices_df = transform_prices(raw_data["prices"], batch_ts)
    prices_df = add_volatility_flag(prices_df)

    trending_df = transform_trending(raw_data["trending"], batch_ts)
    global_df = transform_global(raw_data["global"], batch_ts)

    save_processed(prices_df, "prices")
    save_processed(trending_df, "trending")
    save_processed(global_df, "global")

    return {"prices": prices_df, "trending": trending_df, "global": global_df}


if __name__ == "__main__":
    import json, os
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    # load latest files for testing
    def load_latest(prefix):
        files = sorted([f for f in os.listdir(raw_dir) if f.startswith(prefix)])
        with open(os.path.join(raw_dir, files[-1])) as f:
            return json.load(f)

    raw = {
        "prices": load_latest("prices"),
        "trending": load_latest("trending"),
        "global": load_latest("global"),
    }
    result = run(raw)
    print(result["prices"])
