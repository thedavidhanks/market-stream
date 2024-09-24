This project gets 1 min bars from alpaca and writes them to a database.


A view that groups the 1 min bars as 5 min bars
```
CREATE MATERIALIZED VIEW stock_bars_5min
WITH (timescaledb.continuous) AS
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
```

A Refresh policy that refreshes the view every 5 min.
```
SELECT add_continuous_aggregate_policy('stock_bars_5min',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '5 minutes');
```