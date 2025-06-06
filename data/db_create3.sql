CREATE INDEX idx_stock_bars_5min_bucket_symbol ON stock_bars_5min (bucket, symbol);

ALTER MATERIALIZED VIEW stock_bars_5min
    SET (timescaledb.materialized_only = true);

--- Create refresh policy for stock_bars_5min
SELECT add_continuous_aggregate_policy('stock_bars_5min',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '5 minutes');