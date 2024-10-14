import asyncio
import datetime
import pytz
import os
import re
from alpaca.data.live import StockDataStream
from alpaca.data.models.bars import Bar
from dotenv import load_dotenv

from helpers.database import connect_to_db, add_bar_to_stock_bars, add_trade_to_stock_trades

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
# Database info
DB_PWD = os.getenv("DB_PWD")
DB_URL = os.getenv("DB_URL")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

# ('AAPL','GE','WMT','BA','CSCO','GE','NFLX','MCD')
STOCKS_TO_TRACK = ('AAPL','GE','WMT','BA','CSCO','NFLX','MCD','MSFT','HD','JPM','TSLA','AMZN')

trade_start_hour = 9
trade_start_min = 00
trade_end_hour = 16
trade_end_min = 00
# Define the Eastern Standard Time timezone
est = pytz.timezone('US/Eastern')

def is_trading_hours():

    # Convert the UTC time to Eastern Standard Time
    current_time = datetime.datetime.now(est)
    cur_hr = current_time.hour
    cur_min = current_time.minute

    if current_time.weekday() < 5 and (
        cur_hr> trade_start_hour or  cur_hr == trade_start_hour and cur_min >= trade_start_min
        ) and cur_hr <= trade_end_hour:
        return True
    return  False

async def close_after_trading_hours(wss_client):
    while True:
        current_time = datetime.datetime.now(est)
        if current_time.weekday() < 5 and current_time.hour < trade_end_hour or (current_time.hour == trade_end_hour and current_time.minute < trade_end_min):
            await asyncio.sleep(60)  # Check every minute
        else:
            print("Trading hours have ended. Closing connection...")
            await wss_client.stop_ws()
            # await wss_client.close()
            break

# Create a function that will replace subscribe_bars during non-trading hours.  
# It should take the same arguments as subscribe_bars and call the handler every minute with a random string like, symbol='AAPL' timestamp=datetime.datetime(2024, 9, 23, 19, 59, tzinfo=datetime.timezone.utc) open=226.375 high=226.63 low=226.3 close=226.49 volume=15052.0 trade_count=208.0 vwap=226.463702
def simulate_subscribe_bars(bar_data_handler, *symbols):
    SLEEP_TIME_SEC = 60
    # Every minute, call the bar_data_handler with a random string
    import random
    import datetime

    async def simulate():
        fake_it = True
        while fake_it:
            for symbol in symbols:
                ts_now = repr(datetime.datetime.now(datetime.timezone.utc))
                data = f"symbol='{symbol}' timestamp={ts_now} open={random.uniform(100, 200):.2f} high={random.uniform(100, 200):.2f} low={random.uniform(100, 200):.2f} close={random.uniform(100, 200):.2f} volume={random.randint(100, 200)} trade_count={random.randint(100, 200)} vwap={random.uniform(100, 200):.2f}"
                await bar_data_handler(data)
            if not is_trading_hours():
                fake_it = False
            await asyncio.sleep(SLEEP_TIME_SEC)

    asyncio.run(simulate())

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
        print('Data is not a string or Bar object')
        print(type(data))
    if verbosity >= 2:
        print(data_bar)

    # Connect to the database
    db_connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT)

    # Insert the data into the database
    add_bar_to_stock_bars(data_bar, db_connection)

def add_trade_row_to_db(data, verbosity=0):
    # Connect to the database
    db_connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT)

    # Insert the data into the database
    add_trade_to_stock_trades(data, db_connection)

def bars_string_to_BarClass(data):
    # Convert the string to a dictionary
    result_dict = bars_string_to_dict(data)
    # Create an instance of the Bar class
    bar = Bar(
        t=result_dict['timestamp'],
        o=result_dict['open'],
        h=result_dict['high'],
        l=result_dict['low'],
        c=result_dict['close'],
        v=result_dict['volume'],
        n=result_dict['trade_count'],
        vw=result_dict['vwap']
    )
    return bar

def bars_string_to_dict(data):

    # Regular expression to match key-value pairs
    pattern = r"(\w+)=('[^']*'|datetime\.datetime\([^\)]*\)|[^ ]+)"

    # Find all matches
    matches = re.findall(pattern, data)

    # Convert matches to dictionary
    result_dict = {}
    for key, value in matches:
        if key == 'timestamp':
            # Evaluate the timestamp string to convert it to a datetime object
            value = eval(value)
        result_dict[key] = value
    
    return result_dict

async def live_stock_stream(symbols, verbosity=0, simulate=False, subscribe_trades=False):
    """
    Subscribe to the live stock data stream for the given symbols.

    INPUTS:
    symbols: tuple - The symbols to subscribe to.
    verbosity: int - The level of verbosity for the function. 0 is no output, 1 is errors and warnings, 2 is informational, 3+ is debug.
    """
    
    # Get the OHLCV 1 min bars for the given symbol
    async def bar_data_handler(data):
        if verbosity >=1: print(f'BAR_1MIN: {data}')
        add_bar_row_to_db(data)
    
    async def trade_data_handler(data):
        if verbosity >=1: 
            print(f'TRADE: {data}')   
        add_trade_row_to_db(data)     

    if not is_trading_hours():
        print('Currently outside of trading hours.')
        if simulate:
            print('Simulating data...')
            simulate_subscribe_bars(bar_data_handler, *symbols)
        else:
            print('Guess we\'ll wait...')
    # Subscribe to the live stock data stream
    if verbosity >= 2:
        print('Subscribing to live data...')
    wss_client = StockDataStream(API_KEY, API_SECRET)
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    if subscribe_trades:
        wss_client.subscribe_trades(trade_data_handler, *symbols)

    ## Wait for the trading hours to end, then close the connection  
    # Run the WebSocket client and trading hours check concurrently
    await asyncio.gather(
        asyncio.to_thread(wss_client.run),
        close_after_trading_hours(wss_client)
    )
     
def main():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # If no event loop is present, create a new one and run the main function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        loop.create_task(live_stock_stream(STOCKS_TO_TRACK, verbosity=2))
    else:
        loop.run_until_complete(live_stock_stream(STOCKS_TO_TRACK, verbosity=2))

if __name__== "__main__":
    main()