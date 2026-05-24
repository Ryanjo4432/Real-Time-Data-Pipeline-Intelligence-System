import requests
import json
import os
from datetime import datetime

BASE_URL = "https://api.coingecko.com/api/v3"
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def fetch_prices():
    url = f"{BASE_URL}/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana,cardano,binancecoin",
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_trending():
    url = f"{BASE_URL}/search/trending"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_global_market():
    url = f"{BASE_URL}/global"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def save_raw(data, filename):
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"saved -> {path}")


def run():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    prices = fetch_prices()
    save_raw(prices, f"prices_{ts}.json")

    trending = fetch_trending()
    save_raw(trending, f"trending_{ts}.json")

    global_data = fetch_global_market()
    save_raw(global_data, f"global_{ts}.json")

    return {"prices": prices, "trending": trending, "global": global_data}


if __name__ == "__main__":
    run()
