This project gets 1 min bars from alpaca and writes them to a database.

# Installation

1. Create a postgreSQL database

2. Install the TimescaleDB extension

3. Create the tables.

```
CREATE TABLE stocks_real_time (
  time TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  price DOUBLE PRECISION NULL,
  day_volume INT NULL
);

SELECT create_hypertable('stocks_real_time', by_range('time'));

CREATE INDEX ix_symbol_time ON stocks_real_time (symbol, time DESC);

CREATE TABLE company (
  symbol TEXT NOT NULL,
  name TEXT NOT NULL
);
```


4. Create the view for 5_min bars

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

5. Create a refresh policy for the view.


A Refresh policy that refreshes the view every 5 min.
```
SELECT add_continuous_aggregate_policy('stock_bars_5min',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '5 minutes');
```