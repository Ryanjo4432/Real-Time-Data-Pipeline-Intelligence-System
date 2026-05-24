# Real-Time Market Intelligence Pipeline

Automated crypto data pipeline — pulls live market data from CoinGecko, runs ETL, stores in PostgreSQL, and serves a Streamlit dashboard.

---

## Architecture

```
CoinGecko API → extract.py → transform.py → load.py → PostgreSQL → Streamlit Dashboard
                                                    ↑
                                              scheduler.py (every 5 min)
```

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data Collection | Python + Requests |
| Transformation | Pandas |
| Storage | PostgreSQL |
| Scheduling | schedule library |
| Dashboard | Streamlit + Plotly |

---

## Project Structure

```
market-intelligence-pipeline/
├── data/
│   ├── raw/          # raw JSON from API
│   └── processed/    # cleaned CSVs
├── scripts/
│   ├── extract.py    # API calls
│   ├── transform.py  # cleaning + feature engineering
│   ├── load.py       # DB inserts
│   └── pipeline.py   # orchestrates ETL
├── sql/
│   ├── schema.sql           # DB setup
│   └── analytics_queries.sql
├── dashboard/
│   └── app.py        # Streamlit app
├── scheduler/
│   └── scheduler.py  # runs pipeline every 5 min
├── logs/
├── .env.example
└── requirements.txt
```

---

## Setup

**1. Clone & install**
```bash
git clone https://github.com/Ryanjo4432/Real-Time-Data-Pipeline-Intelligence-System.git
cd Real-Time-Data-Pipeline-Intelligence-System
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# fill in your PostgreSQL credentials
```

**3. Create the database**
```bash
psql -U postgres -f sql/schema.sql
```

**4. Run the pipeline once**
```bash
cd scripts
python pipeline.py
```

**5. Start the scheduler** (runs every 5 min)
```bash
python scheduler/scheduler.py
```

**6. Launch the dashboard**
```bash
streamlit run dashboard/app.py
```

---

## ETL Workflow

### Extract
Hits 3 CoinGecko endpoints:
- `/simple/price` — BTC, ETH, SOL, ADA, BNB prices + market cap + volume
- `/search/trending` — trending coins
- `/global` — total market cap, BTC dominance

### Transform
- Drops nulls, rounds floats
- Calculates 24h % change
- Flags coins with `|change_24h| > 5%` as volatile

### Load
Inserts into 3 tables: `market_metrics`, `trend_analysis`, `global_metrics`

---

## Database Design

```sql
market_metrics   -- price snapshots per coin per run
trend_analysis   -- trending coins per run
global_metrics   -- market-wide stats per run
assets           -- static coin registry
```

---

## Dashboard Features

- Live price cards (BTC, ETH, SOL)
- 24h % change bar chart
- Volume breakdown pie chart
- 7-day BTC price history
- Volatility alerts
- Trending coins table
- Global market cap + BTC dominance

---

## Analytics Queries

See [`sql/analytics_queries.sql`](sql/analytics_queries.sql) for:
- Top movers (biggest % swing)
- Volatility detection
- Hourly price aggregation
- Trending frequency analysis
- Global market cap timeline

---

## Key Insights This System Surfaces

- Which coins are moving abnormally (volatility flag)
- BTC dominance shifts over time
- Volume spikes that precede price moves
- Which coins trend repeatedly

---

## Future Improvements

- [ ] Docker + docker-compose for one-command deploy
- [ ] Apache Airflow for advanced orchestration
- [ ] Email/SMS alerts when BTC drops 5%+
- [ ] Add sentiment data from crypto news APIs
- [ ] Unit tests for each ETL stage
