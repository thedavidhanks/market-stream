import os
from psycopg import sql, connect
from dotenv import load_dotenv

from alpaca.data.models.bars import Bar

from helpers.barConversion import bars_string_to_BarClass

load_dotenv()

# Database info
DB_PWD = os.getenv("MS_DB_PWD")
DB_URL = os.getenv("MS_DB_URL")
DB_USER = os.getenv("MS_DB_USER")
DB_NAME = os.getenv("MS_DB_NAME")
DB_PORT = os.getenv("MS_DB_PORT")

def connect_to_db(user=DB_USER, password=DB_PWD, url=DB_URL, db_name=DB_NAME, port=DB_PORT):
    
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
            AND st.type = 'stock'
            AND st.weight > 0;
        """
        results_list1 = connection.execute(query1).fetchall()

        # Query the DB for stocks that have not been sold.
        query2 = """
        SELECT symbol
        FROM public.orders
        WHERE asset_class = 'us_equity'
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

def get_crypto_to_track():
    """
    Returns a list of symbols of the crypto to track
    
    active_symbols_set is a set of symbols that include all of the following:
    - those that are in the stock_targets table where the weight is greater than 0, type is 'crypto', and they portfolio_id is active.
    - those are are in orders table where the status is open.
    - those that have qty greater than 0 in the orders table for the portfolio_id that is active.
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
            AND st.type = 'crypto'
            AND st.weight > 0;
        """
        results_list1 = connection.execute(query1).fetchall()

        # Query the DB for stocks that have not been sold.
        query2 = """
        SELECT symbol
        FROM public.orders
        WHERE asset_class = 'crypto'
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

def add_bar_row_to_db(data, verbosity=0):
    """
    Connect to the database.
    Add the data_dict keys timestamp, symbol, open, high, low, close, volume, trade_count, vwap to the table, stock_bars
        as time, symbol, open, high, low, close, volume, trade_count, vwap
    
    INPUTS:
        data: string - The data string received from the Alpaca API
        Example data string: "symbol='AAPL' timestamp=datetime.datetime(2024, 9, 23, 19, 59, tzinfo=datetime.timezone.utc) open=226.375 high=226.63 low=226.3 close=226.49 volume=15052.0 trade_count=208.0 vwap=226.463702"
        verbosity: int - The level of verbosity for the function. 0 is no output, 1 is errors and warnings, 2 is informational
    """
    # Convert the string to a dictionary
    if type(data) == str:
        data_bar = bars_string_to_BarClass(data)
    elif type(data) == Bar:
        data_bar = data
    else:
        if verbosity >= 1:
            print(f'Data is not a string or Bar object as expected.  Data type: {type(data)}')
    if verbosity >= 2:
        print(data_bar)

    # Connect to the database
    db_connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT)

    # Insert the data into the database
    add_bar_to_stock_bars(data_bar, db_connection)

def update_bar_row_in_db(data: Bar):
    """
    Connects to the database and if the data with the symbol and timestamp is found, updates the row.
    If the data is not found, adds the data to the database.

    INPUTS:
        data: Bar - The data to add or update in the database
    """

    # Connect to the database
    db_connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT)

    try:
        # Check if the data is in the database
        with db_connection.cursor() as cursor:
            query = sql.SQL(
                "SELECT * FROM {table} WHERE time = %s AND symbol = %s AND interval = %s"
            ).format(
                table=sql.Identifier('stock_bars')
            )
            cursor.execute(
                query,
                (data.timestamp, data.symbol, 1)
            )
            row = cursor.fetchone()

        # If the data is found, update the row
        if row:
            with db_connection.cursor() as cursor:
                query = sql.SQL(
                    "UPDATE {table} SET open = %s, high = %s, low = %s, close = %s, volume = %s, trade_count = %s, vwap = %s WHERE time = %s AND symbol = %s AND interval = %s"
                ).format(
                    table=sql.Identifier('stock_bars')
                )
                cursor.execute(
                    query,
                    (data.open, data.high, data.low, data.close, data.volume, data.trade_count, data.vwap, data.timestamp, data.symbol, 1)
                )
            db_connection.commit()
        # If the data is not found, add the data to the database
        else:
            add_bar_to_stock_bars(data, db_connection)
    finally:
        # Ensure the connection is closed
        db_connection.close()