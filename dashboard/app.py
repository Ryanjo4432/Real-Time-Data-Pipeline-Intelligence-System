import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Crypto Intelligence Dashboard", layout="wide")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "market_intelligence"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


@st.cache_data(ttl=60)
def query(sql):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


st.title("Crypto Market Intelligence Pipeline")
st.caption("Live data — refreshes every 60s")

# latest snapshot
latest = query("""
    SELECT coin_id, price_usd, change_24h, volume_24h, is_volatile, fetched_at
    FROM market_metrics
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM market_metrics)
    ORDER BY market_cap DESC
""")

col1, col2, col3 = st.columns(3)
if not latest.empty:
    btc = latest[latest["coin_id"] == "bitcoin"]
    eth = latest[latest["coin_id"] == "ethereum"]
    sol = latest[latest["coin_id"] == "solana"]

    col1.metric("Bitcoin", f"${btc['price_usd'].values[0]:,.2f}" if not btc.empty else "N/A",
                f"{btc['change_24h'].values[0]:.2f}%" if not btc.empty else "")
    col2.metric("Ethereum", f"${eth['price_usd'].values[0]:,.2f}" if not eth.empty else "N/A",
                f"{eth['change_24h'].values[0]:.2f}%" if not eth.empty else "")
    col3.metric("Solana", f"${sol['price_usd'].values[0]:,.2f}" if not sol.empty else "N/A",
                f"{sol['change_24h'].values[0]:.2f}%" if not sol.empty else "")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("24h Price Movement")
    fig = px.bar(latest, x="coin_id", y="change_24h",
                 color="change_24h", color_continuous_scale="RdYlGn",
                 labels={"change_24h": "% Change", "coin_id": "Coin"})
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Volume 24h")
    fig2 = px.pie(latest, names="coin_id", values="volume_24h")
    st.plotly_chart(fig2, use_container_width=True)

# BTC price history
st.subheader("Bitcoin — 7 Day Price History")
btc_hist = query("""
    SELECT DATE_TRUNC('hour', fetched_at) AS hour, AVG(price_usd) AS avg_price
    FROM market_metrics
    WHERE coin_id = 'bitcoin' AND fetched_at >= NOW() - INTERVAL '7 days'
    GROUP BY 1 ORDER BY 1
""")
if not btc_hist.empty:
    fig3 = px.line(btc_hist, x="hour", y="avg_price", labels={"avg_price": "USD", "hour": ""})
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("not enough history yet — keep the pipeline running")

# volatility alerts
st.subheader("Volatility Alerts (last hour)")
volatile = latest[latest["is_volatile"] == True]
if volatile.empty:
    st.success("no volatile coins right now")
else:
    st.warning(f"{len(volatile)} coin(s) showing unusual movement")
    st.dataframe(volatile[["coin_id", "change_24h", "volume_24h"]])

# trending
st.subheader("Trending Coins")
trending = query("""
    SELECT coin_id, name, symbol, market_cap_rank, fetched_at
    FROM trend_analysis
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM trend_analysis)
""")
if not trending.empty:
    st.dataframe(trending, use_container_width=True)

# global metrics
st.subheader("Global Market")
glb = query("SELECT * FROM global_metrics ORDER BY fetched_at DESC LIMIT 1")
if not glb.empty:
    g = glb.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Market Cap", f"${g['total_market_cap_usd']/1e12:.2f}T")
    c2.metric("BTC Dominance", f"{g['btc_dominance']:.1f}%")
    c3.metric("Active Coins", f"{int(g['active_coins']):,}")
