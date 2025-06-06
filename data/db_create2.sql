--- MATERIALIZED VIEW stock_bars_5min creation
CREATE MATERIALIZED VIEW stock_bars_5min WITH (timescaledb.continuous) AS
    SELECT
        time_bucket('5 minutes', time) AS bucket,
        symbol,
        first(open, time) AS open,
        max(high) AS high,
        min(low) AS low,
        last(close, time) AS close,
        sum(volume) AS volume
FROM stock_bars
GROUP BY bucket, symbol;

