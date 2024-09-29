from psycopg import sql, connect

def connect_to_db(user, password, url, db_name):
    
    # REFERENCE - https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    db_connection = connect(host=url, port=5434, dbname=db_name, user=user, password=password)

    return db_connection

def add_bar_to_stock_bars(data_bar, connection):
    required_props = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
    
    # Check if all required properties are present in the data_bar
    missing_props = [prop for prop in required_props if not hasattr(data_bar, prop)]
    
    if missing_props:
        raise ValueError(f'All required properties are not present in the data_bar. Missing properties: {missing_props}')
    
    # Insert the data into the database
    with connection.cursor() as cursor:
        query = sql.SQL(
            "INSERT INTO {table} (time, symbol, open, high, low, close, volume, trade_count, vwap, interval) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        ).format(
            table=sql.Identifier('stock_bars')
        )
        cursor.execute(
            query,
            (data_bar.timestamp, data_bar.symbol, data_bar.open, data_bar.high, data_bar.low, data_bar.close, data_bar.volume, data_bar.trade_count, data_bar.vwap, 1)
        )

    connection.commit()

def add_trade_to_stock_trades(data, connection):
    required_props = ['symbol', 'timestamp', 'exchange', 'price', 'size', 'id', 'conditions']

    # Check if all required properties are present in the data
    missing_props = [prop for prop in required_props if not hasattr(data, prop)]

    if missing_props:
        raise ValueError(f'All required properties are not present in the data. Missing properties: {missing_props}')
    
    # Insert the data into the database
    with connection.cursor() as cursor:
        query = sql.SQL(
            "INSERT INTO {table} (symbol, time, exchange, price, size, trade_id, conditions) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        ).format(
            table=sql.Identifier('stock_trades_real_time')
        )
        cursor.execute(
            query,
            (data.symbol, data.timestamp, data.exchange, data.price, data.size, data.id, data.conditions)
        )

    connection.commit()
    
# Connect to the database and refresh the view stock_bars_5min
def refresh_stock_bars_5min(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            "CALL refresh_continuous_aggregate('stock_bars_5min', NULL, NULL)"
        )
    connection.commit()
