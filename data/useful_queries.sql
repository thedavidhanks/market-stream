SELECT COUNT(*) FROM public.stock_bars_historical
-- SELECT timestamp, * FROM public.stock_bars_historical ORDER BY timestamp ASC
-- DELETE FROM public.stock_bars_historical
-- ALTER TABLE stock_bars_historical
-- ADD CONSTRAINT unique_time_symbol_interval UNIQUE (timestamp, symbol, interval);
-- SELECT pg_size_pretty(pg_database_size('postgres'));
-- SELECT pg_size_pretty(pg_relation_size('public.stock_bars_historical'));