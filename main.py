import argparse
import asyncio
import datetime
import pytz
import os

from alpaca.data.live import StockDataStream, CryptoDataStream

from dotenv import load_dotenv

from helpers.database import connect_to_db, add_bar_row_to_db, add_trade_to_stock_trades, get_stocks_to_track, update_bar_row_in_db, get_crypto_to_track
from helpers.stringHelper import bar_to_oneline_string

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("MS_ALPACA_API_KEY")
API_SECRET = os.getenv("MS_ALPACA_API_SECRET")

CHECK_FREQUENCY = 300  # 5 minutes

trade_start_hour = 9
trade_start_min = 00
trade_end_hour = 16
trade_end_min = 00
# Define the Eastern Standard Time timezone
est = pytz.timezone('US/Eastern')

def is_trading_hours():
    # True if it is a weekday and the current time is between 9:30 AM and 4:00 PM EST

    # Convert the UTC time to Eastern Standard Time
    current_time = datetime.datetime.now(est)
    start_time = current_time.replace(hour=trade_start_hour, minute=trade_start_min, second=0, microsecond=0)
    end_time = current_time.replace(hour=trade_end_hour, minute=trade_end_min, second=0, microsecond=0)

    if current_time.weekday() < 5 and start_time <= current_time <= end_time:
        return True
    return  False

async def close_after_trading_hours(wss_client, verbosity=0):
    # sleep for 5 seconds to allow the client to start
    await asyncio.sleep(5)

    while True:
        if is_trading_hours():
            await asyncio.sleep(60)  # Check every minute
        else:
            if verbosity >= 2:
                print("Trading hours have ended. Closing connection...")
            await wss_client.stop_ws()
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

def add_trade_row_to_db(data):
    # Connect to the database
    db_connection = connect_to_db()

    # Insert the data into the database
    add_trade_to_stock_trades(data, db_connection)

    db_connection.close()

async def live_stock_stream(symbols, verbosity=0, simulate=False, subscribe_trades=False):
    """
    Subscribe to the live stock data stream for the given symbols.

    INPUTS:
    symbols: tuple - The symbols to subscribe to.
    verbosity: int - The level of verbosity for the function. 0 is no output, 1 is errors and warnings, 2 is informational, 3+ is debug.
    """
        
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
    wss_client.subscribe_updated_bars(updatebar_data_handler, *symbols)
    if subscribe_trades:
        wss_client.subscribe_trades(trade_data_handler, *symbols)

    ## Wait for the trading hours to end, then close the connection  
    # Run the WebSocket client and trading hours check concurrently
    await asyncio.gather(
        asyncio.to_thread(wss_client.run),
        close_after_trading_hours(wss_client)
    )

def run_wss_client(wss_client, verbosity=1):
    try:
        wss_client.run()
    except ValueError as e:
        if "connection limit exceeded" in str(e):
            if verbosity >= 1:
                print(f"ValueError (connection limit) running wss_client: {e}")
            os._exit(1)
        else:
            if verbosity >= 1:
                print(f"ValueError running wss_client: {e}")
            raise
    except Exception as e:
        print(f"Error running wss_client: {e}")
        os._exit(1)

# Get the OHLCV 1 min bars for the given symbol
async def bar_data_handler(data):
    print(f'BAR_1MIN: {bar_to_oneline_string(data)}')
    add_bar_row_to_db(data)

async def updatebar_data_handler(data):
    print(f'UPDATE_BAR: {bar_to_oneline_string(data)}')
    update_bar_row_in_db(data)

def start_sub(stocks_to_track=None, asset='stock', verbosity=0):
    """
    Start the WebSocket client and subscribe to the bars for the symbols to track.

    Alpaca provides sandbox urls for testing, but does not explain how to connect to them.
    stock_url = "wss://stream.data.sandbox.alpaca.markets/v2/iex"
    crypto_url = "wss://stream.data.sandbox.alpaca.markets/v1beta3/crypto/us"
    """
    symbols = get_stocks_to_track() if stocks_to_track is None else stocks_to_track
    
    try:
        if asset == 'stock':
            wss_client = StockDataStream(API_KEY, API_SECRET)
        elif asset == 'crypto':
            wss_client = CryptoDataStream(API_KEY, API_SECRET)
    except Exception as e:
        if verbosity >=1: print(f"Failed to connect to the data stream: {e}")
        exit(1)
    
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    wss_client.subscribe_updated_bars(updatebar_data_handler, *symbols)
    return wss_client

def update_sub(client, new_symbols, old_symbols):
    # update the subscriptions to the new symbols
    client.unsubscribe_bars(*old_symbols)
    client.subscribe_bars(bar_data_handler, *new_symbols)

    # update the corrected subscriptions to the new symbols
    client.unsubscribe_updated_bars(*old_symbols)
    client.subscribe_updated_bars(updatebar_data_handler, *new_symbols)

async def update_symbols(wss_client, symbols_to_track=(), verbosity=1):
    current_stocks_to_track = symbols_to_track

    while True:
        if is_trading_hours():
            if verbosity >=2:
                print(f'update_symbols: sleeping for {CHECK_FREQUENCY} secs...')
            await asyncio.sleep(CHECK_FREQUENCY)  # Sleep for 5 minutes
            new_stocks_to_track = get_stocks_to_track()
            if sorted(current_stocks_to_track) != sorted(new_stocks_to_track):
                if verbosity >=2:
                    print(f'update_symbols: Updating stocks to track...now tracking {new_stocks_to_track}')
                old_stocks = set(current_stocks_to_track)
                update_sub(wss_client, new_stocks_to_track, old_stocks)
                current_stocks_to_track = new_stocks_to_track
            else:
                if verbosity >=2:
                    print('update_symbols: No changes to stocks to track')
        else:
            if verbosity >=2:
                print('update_symbols: Currently outside of trading hours. Exiting...')
            break

async def update_crypto_symbols(wss_client, symbols_to_track=(), verbosity=1):
    current_crypto_to_track = symbols_to_track

    while True:
        if verbosity >=2:
            print(f'update_crypto_symbols: sleeping for {CHECK_FREQUENCY} secs...')
        await asyncio.sleep(CHECK_FREQUENCY)  # Sleep for 5 minutes
        new_crypto_to_track = get_crypto_to_track()
        if sorted(current_crypto_to_track) != sorted(new_crypto_to_track):
            if verbosity >=2:
                print(f'update_crypto_symbols: Updating crypto to track...now tracking {new_crypto_to_track}')
            old_crypto = set(current_crypto_to_track)
            update_sub(wss_client, new_crypto_to_track, old_crypto)
            current_crypto_to_track = new_crypto_to_track
        else:
            if verbosity >=2:
                print('update_crypto_symbols: No changes to crypto to track')

async def sub_bars(verbosity=0):
    """
    start 3 tasks:
    - run_wss_client: starts a client that is connected to alpaca's websocket
    - update_symbols: updates the symbols to track at a specified interval.
    - close_after_trading_hours: closes the connection after trading hours.
    """
    stock_symbols = get_stocks_to_track()
    crypto_symbols = get_crypto_to_track()
    
    # A stock data stream client
    wss_stock_client = start_sub(stocks_to_track=stock_symbols, asset='stock', verbosity=verbosity)

    # A crypto data stream client
    wss_crypto_client = start_sub(stocks_to_track=crypto_symbols, asset='crypto', verbosity=verbosity)

    try:
        await asyncio.gather(
            # thread for tracking stock data
            asyncio.to_thread(run_wss_client, wss_stock_client, verbosity=verbosity),
            update_symbols(wss_stock_client, symbols_to_track=stock_symbols, verbosity=verbosity),
            close_after_trading_hours(wss_stock_client, verbosity=verbosity),

            # thread for tracking crypto data
            asyncio.to_thread(run_wss_client, wss_crypto_client, verbosity=verbosity),
            update_crypto_symbols(wss_crypto_client, symbols_to_track=crypto_symbols, verbosity=verbosity)
        )
    except asyncio.CancelledError:
        print("Subscription interrupted")
    except ValueError as e:
        if "connection limit exceeded" in str(e):
            print(f"Error in sub_bars: {e}")
            os._exit(1)
        else:
            raise
    except Exception as e:
        print(f"Error in sub_bars: {e}")
        os._exit(1)
    finally:
        wss_stock_client.stop()
        wss_crypto_client.stop()

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Capture the market data in a database.')
    
    # Add arguments
    parser.add_argument('-v', '--verbosity', help='Set output verbosity level. 0 None, 1 Errors, 2 Info, 3 Debug', type=int, default=0)

    # Parse the arguments
    args = parser.parse_args()

    try:
        asyncio.run(sub_bars(verbosity=args.verbosity))
    except KeyboardInterrupt:
        print("Program interrupted")

if __name__== "__main__":
    main()