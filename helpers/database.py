from psycopg import sql, connect

def connect_to_db(user, password, url, db_name):
    
    # REFERENCE - https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    db_connection = connect(host=url, port=5434, dbname=db_name, user=user, password=password)

    return db_connection

def add_bar_to_stock_bars(data_dict, connection):
    required_keys = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
    
    # Check if all required keys are present in the data_dict
    if not all(key in data_dict for key in required_keys):
        # find the missing keys
        missing_keys = list(set(required_keys) - set(data_dict.keys()))

        raise ValueError(f'All required keys are not present in the data_dict. Missing keys: {missing_keys}')
    
    # Insert the data into the database
    with connection.cursor() as cursor:
        query = sql.SQL(
            "INSERT INTO {table} (time, symbol, open, high, low, close, volume, trade_count, vwap) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        ).format(
            table=sql.Identifier('stock_bars')
        )
        cursor.execute(
            query,
            (data_dict['timestamp'], data_dict['symbol'], data_dict['open'], data_dict['high'], data_dict['low'], data_dict['close'], data_dict['volume'], data_dict['trade_count'], data_dict['vwap'])
        )

    connection.commit()
