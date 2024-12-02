import os
from psycopg import sql, connect
from dotenv import load_dotenv

load_dotenv()

# Database info
DB_PWD = os.getenv("MS_DB_PWD")
DB_URL = os.getenv("MS_DB_URL")
DB_USER = os.getenv("MS_DB_USER")
DB_NAME = os.getenv("MS_DB_NAME")
DB_PORT = os.getenv("MS_DB_PORT")

def connect_to_db(user, password, url, db_name, port=5434):
    
    # REFERENCE - https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    db_connection = connect(host=url, port=port, dbname=db_name, user=user, password=password)

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

# Connect to the database and print 10 rows from the stock_bars_5min view
def print_stock_bars_5min(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM stock_bars_5min LIMIT 10"
        )
        rows = cursor.fetchall()
        for row in rows:
            print(row)

def get_stocks_to_track():
    """
    Returns a list of symbols of the stocks to track
    
    active_symbols_set is a set of symbols that include all of the following:
    - those that are in the stock_targets table where the weight is greater than 0 and they portfolio_id is active.
    - those are are in orders table where the status is open.
    - those that have qty greater than 0 in the orders table for the portfolio_id that is active.
    TODO: Only the top condition is implemented for now.  Add in the other conditions.
    """

    with connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT) as connection:
        # Query the DB for the active portfolios and get the symbols that are in the stock_targets table.
        query1 = """
        SELECT DISTINCT
            st.symbol
        FROM 
            public.portfolio_configs pc
        JOIN 
            public.stock_targets st
        ON 
            pc.id = st.portfolio_id
        WHERE 
            pc.active = TRUE
            AND st.weight > 0;
        """
        results_list1 = connection.execute(query1).fetchall()

        # Query the DB for stocks that have not been sold.
        query2 = """
        SELECT symbol
        FROM public.orders
        GROUP BY symbol
        HAVING SUM(CASE WHEN side = 'buy' THEN qty::numeric ELSE 0 END) - 
               SUM(CASE WHEN side = 'sell' THEN qty::numeric ELSE 0 END) > 0;
        """
        results_list2 = connection.execute(query2).fetchall()

        # Use a set to avoid duplicates
        active_symbols_set = set(result[0] for result in results_list1)
        active_symbols_set.update(result[0] for result in results_list2)

        # sort the set alphabetically
        active_symbols_set = sorted(active_symbols_set)

    return tuple(active_symbols_set)