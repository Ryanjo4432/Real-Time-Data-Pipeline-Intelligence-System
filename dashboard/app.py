import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Crypto Intelligence",
    layout="wide",
    menu_items={}  # removes the deploy button
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "market_intelligence"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

DARK = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.05)"


@st.cache_data(ttl=60)
def query(sql):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


# ── header ────────────────────────────────────────────────────────────────────
st.title("Crypto Market Intelligence")
st.caption("Auto-refreshes every 60s · data pulled every 5 min from CoinGecko")

# ── latest snapshot ────────────────────────────────────────────────────────────
latest = query("""
    SELECT coin_id, price_usd, change_24h, volume_24h, market_cap, is_volatile, fetched_at
    FROM market_metrics
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM market_metrics)
    ORDER BY market_cap DESC
""")

# metric cards
col1, col2, col3, col4, col5 = st.columns(5)
cards = [col1, col2, col3, col4, col5]
coins_order = ["bitcoin", "ethereum", "binancecoin", "solana", "cardano"]

for col, cid in zip(cards, coins_order):
    row = latest[latest["coin_id"] == cid]
    if not row.empty:
        r = row.iloc[0]
        col.metric(
            cid.capitalize() if cid != "binancecoin" else "BNB",
            f"${r['price_usd']:,.2f}",
            f"{r['change_24h']:+.2f}%"
        )

st.divider()

# ── charts row ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("24h Price Movement")
    if not latest.empty:
        colors = ["#2ecc71" if x >= 0 else "#e74c3c" for x in latest["change_24h"]]
        fig = go.Figure(go.Bar(
            x=latest["coin_id"],
            y=latest["change_24h"],
            marker_color=colors,
            text=[f"{v:+.2f}%" for v in latest["change_24h"]],
            textposition="outside",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK,
            plot_bgcolor=DARK,
            yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor="rgba(255,255,255,0.2)"),
            xaxis=dict(showgrid=False),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Market Cap Share")
    if not latest.empty:
        fig2 = go.Figure(go.Pie(
            labels=latest["coin_id"],
            values=latest["market_cap"],
            hole=0.5,
            marker=dict(colors=["#F7931A", "#627EEA", "#F3BA2F", "#9945FF", "#0033AD"]),
            textinfo="label+percent",
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK,
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── BTC 7-day history ──────────────────────────────────────────────────────────
st.subheader("Bitcoin — 7 Day Price History")
btc_hist = query("""
    SELECT DATE_TRUNC('hour', fetched_at) AS hour, AVG(price_usd) AS avg_price
    FROM market_metrics
    WHERE coin_id = 'bitcoin' AND fetched_at >= NOW() - INTERVAL '7 days'
    GROUP BY 1 ORDER BY 1
""")

if not btc_hist.empty and len(btc_hist) > 1:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=btc_hist["hour"],
        y=btc_hist["avg_price"],
        line=dict(color="#F7931A", width=2, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(247,147,26,0.08)",
    ))
    fig3.update_layout(
        template="plotly_dark",
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        yaxis=dict(showgrid=True, gridcolor=GRID, tickformat="$,.0f"),
        xaxis=dict(showgrid=False),
        margin=dict(l=0, r=0, t=10, b=0),
        height=250,
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("keep the pipeline running — history builds up over time")

# ── bottom row ─────────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Volatility Alerts")
    volatile = latest[latest["is_volatile"] == True]
    if volatile.empty:
        st.success("no coins flagged right now")
    else:
        st.warning(f"{len(volatile)} coin(s) moving abnormally")
        st.dataframe(
            volatile[["coin_id", "change_24h", "volume_24h"]].rename(columns={
                "coin_id": "Coin", "change_24h": "% Change", "volume_24h": "Volume"
            }),
            use_container_width=True, hide_index=True
        )

with col_b:
    st.subheader("Trending Coins")
    trending = query("""
        SELECT coin_id, name, symbol, market_cap_rank
        FROM trend_analysis
        WHERE fetched_at = (SELECT MAX(fetched_at) FROM trend_analysis)
        ORDER BY market_cap_rank ASC NULLS LAST
    """)
    if not trending.empty:
        st.dataframe(trending, use_container_width=True, hide_index=True)

# ── global metrics ─────────────────────────────────────────────────────────────
st.subheader("Global Market")
glb = query("SELECT * FROM global_metrics ORDER BY fetched_at DESC LIMIT 1")
if not glb.empty:
    g = glb.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Market Cap", f"${g['total_market_cap_usd']/1e12:.2f}T")
    c2.metric("BTC Dominance", f"{g['btc_dominance']:.1f}%")
    c3.metric("Active Coins", f"{int(g['active_coins']):,}")

# ── auto refresh every 60s ─────────────────────────────────────────────────────
time.sleep(60)
st.rerun()
