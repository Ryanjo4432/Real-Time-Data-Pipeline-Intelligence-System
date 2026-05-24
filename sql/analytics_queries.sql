-- latest price snapshot
SELECT coin_id, price_usd, change_24h, volume_24h, is_volatile, fetched_at
FROM market_metrics
WHERE fetched_at = (SELECT MAX(fetched_at) FROM market_metrics)
ORDER BY market_cap DESC;

-- top movers last 24h (biggest % swing)
SELECT coin_id, AVG(change_24h) AS avg_change, MAX(price_usd) AS high, MIN(price_usd) AS low
FROM market_metrics
WHERE fetched_at >= NOW() - INTERVAL '24 hours'
GROUP BY coin_id
ORDER BY ABS(AVG(change_24h)) DESC;

-- volatility alerts (flagged coins)
SELECT DISTINCT coin_id, change_24h, fetched_at
FROM market_metrics
WHERE is_volatile = TRUE
  AND fetched_at >= NOW() - INTERVAL '1 hour'
ORDER BY fetched_at DESC;

-- 7-day price history for BTC
SELECT DATE_TRUNC('hour', fetched_at) AS hour, AVG(price_usd) AS avg_price
FROM market_metrics
WHERE coin_id = 'bitcoin'
  AND fetched_at >= NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 1;

-- how many times each coin trended
SELECT coin_id, name, COUNT(*) AS trend_count
FROM trend_analysis
GROUP BY coin_id, name
ORDER BY trend_count DESC
LIMIT 10;

-- global market cap trend
SELECT DATE_TRUNC('hour', fetched_at) AS hour, AVG(total_market_cap_usd) AS market_cap, AVG(btc_dominance) AS btc_dom
FROM global_metrics
GROUP BY 1
ORDER BY 1 DESC
LIMIT 48;
