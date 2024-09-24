import asyncio
import datetime
import pytz
import os
import re
from alpaca.data.live import StockDataStream
from alpaca.data.models.bars import Bar
from dotenv import load_dotenv

from helpers.database import connect_to_db, add_bar_to_stock_bars

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
# Database info
DB_PWD = os.getenv("DB_PWD")
DB_URL = os.getenv("DB_URL")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")


def is_trading_hours():
    # Define the Eastern Standard Time timezone
    est = pytz.timezone('US/Eastern')

    # Get the current time in UTC
    utc_time = datetime.datetime.now(datetime.timezone.utc)

    # Convert the UTC time to Eastern Standard Time
    current_time = utc_time.astimezone(est)
    if current_time.weekday() < 5 and current_time.hour >= 9 and current_time.hour < 16:
        return True
    return  False

def live_alpaca_bars(symbols='AAPL', verbosity=0, simulate=False):
    
    # Get the OHLCV 1 min bars for the given symbol
    async def bar_data_handler(data):
        if verbosity >=1: print(data)
        add_row_to_db(data)

    if not is_trading_hours():
        print('IDIOT! Not trading hours.')
        if simulate:
            print('Simulating data...')
            simulate_subscribe_bars(bar_data_handler, *symbols)
        else:
            print('Guess we\'ll wait...')
    # Subscribe to the live stock data stream
    wss_client = StockDataStream(API_KEY, API_SECRET)
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    wss_client.run()

# Create a function that will replace subscribe_bars during non-trading hours.  
# It should take the same arguments as subscribe_bars and call the handler every minute with a random string like, symbol='AAPL' timestamp=datetime.datetime(2024, 9, 23, 19, 59, tzinfo=datetime.timezone.utc) open=226.375 high=226.63 low=226.3 close=226.49 volume=15052.0 trade_count=208.0 vwap=226.463702
def simulate_subscribe_bars(bar_data_handler, *symbols):
    SLEEP_TIME_SEC = 60
    # Every minute, call the bar_data_handler with a random string
    import random
    import datetime

    async def simulate():
        while True:
            for symbol in symbols:
                ts_now = repr(datetime.datetime.now(datetime.timezone.utc))
                data = f"symbol='{symbol}' timestamp={ts_now} open={random.uniform(100, 200):.2f} high={random.uniform(100, 200):.2f} low={random.uniform(100, 200):.2f} close={random.uniform(100, 200):.2f} volume={random.randint(100, 200)} trade_count={random.randint(100, 200)} vwap={random.uniform(100, 200):.2f}"
                await bar_data_handler(data)
            await asyncio.sleep(SLEEP_TIME_SEC)

    asyncio.run(simulate())

def add_row_to_db(data, verbosity=0):
    # Connect to the database.
    # Add the data_dict keys timestamp, symbol, open, high, low, close, volume, trade_count, vwap to the table, stock_bars
    #  as time, symbol, open, high, low, close, volume, trade_count, vwap
    #
    # Inputs:
    # data: string - The data string received from the Alpaca API
    # Example data string: "symbol='AAPL' timestamp=datetime.datetime(2024, 9, 23, 19, 59, tzinfo=datetime.timezone.utc) open=226.375 high=226.63 low=226.3 close=226.49 volume=15052.0 trade_count=208.0 vwap=226.463702"

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
    db_connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME)

    # Insert the data into the database
    add_bar_to_stock_bars(data_bar, db_connection)

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

if __name__== "__main__":
    live_alpaca_bars(('AAPL','GE'), verbosity=1)