import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
from collections import deque

st.set_page_config(page_title="Live Charts", layout="wide", menu_items={})

MAX_POINTS = 60  # 60 seconds of rolling history

COINS = {
    "BTCUSDT": {"name": "Bitcoin",  "symbol": "BTC", "color": "#F7931A"},
    "ETHUSDT": {"name": "Ethereum", "symbol": "ETH", "color": "#627EEA"},
    "SOLUSDT": {"name": "Solana",   "symbol": "SOL", "color": "#9945FF"},
}

DARK = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.04)"


@st.cache_data(ttl=10)
def fetch_24h_stats():
    try:
        syms = str(list(COINS.keys())).replace("'", '"')
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            params={"symbols": syms},
            timeout=3
        )
        return {item["symbol"]: item for item in r.json()}
    except:
        return {}


def fetch_prices():
    try:
        syms = str(list(COINS.keys())).replace("'", '"')
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbols": syms},
            timeout=2
        )
        return {item["symbol"]: float(item["price"]) for item in r.json()}
    except:
        return {}


# init rolling history in session state
if "hist" not in st.session_state:
    st.session_state.hist = {sym: deque(maxlen=MAX_POINTS) for sym in COINS}
    st.session_state.ts   = deque(maxlen=MAX_POINTS)

# pull latest prices
prices = fetch_prices()
stats  = fetch_24h_stats()
now    = datetime.utcnow()

for sym, price in prices.items():
    st.session_state.hist[sym].append(price)
st.session_state.ts.append(now)

# ── header ────────────────────────────────────────────────────────────────────
st.title("Live Price Feed")
st.caption(f"Binance · updates every second · {now.strftime('%H:%M:%S')} UTC")

# ── metric cards ───────────────────────────────────────────────────────────────
cols = st.columns(len(COINS))
for col, (sym, info) in zip(cols, COINS.items()):
    hist = list(st.session_state.hist[sym])
    stat = stats.get(sym, {})
    change_pct = float(stat.get("priceChangePercent", 0))
    high_24 = float(stat.get("highPrice", 0))
    low_24  = float(stat.get("lowPrice", 0))

    if hist:
        col.metric(
            f"{info['name']}  ({info['symbol']})",
            f"${hist[-1]:,.2f}",
            f"{change_pct:+.2f}%  24h"
        )
        col.caption(f"24h High  ${high_24:,.2f}   ·   Low  ${low_24:,.2f}")

st.divider()

# ── live charts ────────────────────────────────────────────────────────────────
timestamps = list(st.session_state.ts)

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    subplot_titles=[info["name"] for info in COINS.values()],
)

for i, (sym, info) in enumerate(COINS.items(), 1):
    hist = list(st.session_state.hist[sym])
    ts   = timestamps[-len(hist):]
    if not hist:
        continue

    r, g, b = int(info["color"][1:3], 16), int(info["color"][3:5], 16), int(info["color"][5:7], 16)

    fig.add_trace(
        go.Scatter(
            x=ts,
            y=hist,
            name=info["name"],
            mode="lines",
            line=dict(color=info["color"], width=2, shape="spline"),
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.08)",
            hovertemplate=f"<b>%{{y:$,.2f}}</b><br>%{{x|%H:%M:%S}}<extra>{info['name']}</extra>",
        ),
        row=i, col=1
    )

    # latest price annotation on the right
    if hist:
        fig.add_annotation(
            x=timestamps[-1] if timestamps else 0,
            y=hist[-1],
            text=f"  ${hist[-1]:,.2f}",
            showarrow=False,
            font=dict(color=info["color"], size=12, family="monospace"),
            xanchor="left",
            row=i, col=1
        )

fig.update_layout(
    height=620,
    template="plotly_dark",
    paper_bgcolor=DARK,
    plot_bgcolor="rgba(14,17,23,0.6)",
    showlegend=False,
    margin=dict(l=10, r=100, t=30, b=10),
    font=dict(family="monospace", size=11),
)
fig.update_xaxes(showgrid=False, showticklabels=False)
fig.update_yaxes(
    showgrid=True,
    gridcolor=GRID,
    tickformat="$,.2f",
    side="right",
    tickfont=dict(size=10),
)
fig.update_annotations(font_size=11)

st.plotly_chart(fig, use_container_width=True)

# ── volume bar (last 60s simulated from 24h volume) ───────────────────────────
st.subheader("24h Volume")
if stats:
    vol_data = {
        COINS[sym]["name"]: float(stats[sym].get("quoteVolume", 0))
        for sym in COINS if sym in stats
    }
    fig_vol = go.Figure(go.Bar(
        x=list(vol_data.keys()),
        y=list(vol_data.values()),
        marker_color=["#F7931A", "#627EEA", "#9945FF"],
        text=[f"${v/1e9:.2f}B" for v in vol_data.values()],
        textposition="outside",
    ))
    fig_vol.update_layout(
        template="plotly_dark",
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        height=220,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(showgrid=True, gridcolor=GRID, tickformat="$,.0f"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# ── tick every second ─────────────────────────────────────────────────────────
time.sleep(1)
st.rerun()
