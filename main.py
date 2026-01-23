import argparse
import asyncio
import datetime
import pytz
import os

from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca.data.live.websocket import DataStream

from dotenv import load_dotenv

from helpers.database import connect_to_db, add_bar_row_to_db, add_trade_to_stock_trades, get_stocks_to_track, update_bar_row_in_db, get_crypto_to_track
from helpers.stringHelper import bar_to_oneline_string
from helpers.datastream_helper import test_socket, get_wss_url
from helpers.logger import logger, set_file_log_level

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("MS_ALPACA_API_KEY", default="")
API_SECRET = os.getenv("MS_ALPACA_API_SECRET", default="")

CHECK_FREQUENCY = 300  # 5 minutes
TESTING = False

# Alpaca supports extended trading hours from 4:00 AM to 8:00 PM EST
# https://docs.alpaca.markets/docs/orders-at-alpaca#orders-submitted-outside-of-eligible-trading-hours
# Define the trading hours
trade_start_hour = 4
trade_start_min = 00
trade_end_hour = 20
trade_end_min = 00
est = pytz.timezone('US/Eastern')

def is_trading_hours():
    # True if it is a weekday and the current time is between 9:30 AM and 4:00 PM EST

    # Convert the UTC time to Eastern Standard Time
    current_time = datetime.datetime.now(est)
    start_time = current_time.replace(hour=trade_start_hour, minute=trade_start_min, second=0, microsecond=0)
    end_time = current_time.replace(hour=trade_end_hour, minute=trade_end_min, second=0, microsecond=0)

    # It is a weekday and the current time is between 9:30 AM and 4:00 PM EST
    if current_time.weekday() < 5 and start_time <= current_time <= end_time:
        return True
    return  False

async def close_after_trading_hours(wss_client):
    # sleep for 5 seconds to allow the client to start
    await asyncio.sleep(5)

    while True:
        if is_trading_hours():
            await asyncio.sleep(60)  # Check every minute

        else:
            logger.info("Trading hours have ended. Closing connection...")
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

async def live_stock_stream(symbols, simulate=False, subscribe_trades=False):
    """
    Subscribe to the live stock data stream for the given symbols.

    INPUTS:
    symbols: tuple - The symbols to subscribe to.
    """
        
    async def trade_data_handler(data):
        logger.info(f'TRADE: {data}')
        add_trade_row_to_db(data)     

    if not is_trading_hours():
        logger.info('live_stock_stream: Currently outside of trading hours.')
        if simulate:
            logger.info('Simulating data...')
            simulate_subscribe_bars(bar_data_handler, *symbols)
        else:
            logger.info('Guess we\'ll wait...')
    # Subscribe to the live stock data stream
    logger.info('Subscribing to live data...')
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

def run_wss_client(wss_client: DataStream, client_type="unknown"):
    if wss_client is None:
        logger.error("Error: WebSocket client is None. Exiting run_wss_client.")
        return
    try:
        wss_client.run()
    except ValueError as e:
        if "connection limit exceeded" in str(e):
            logger.error(f"run_wss_client: ValueError (connection limit) {e}")
        else:
            logger.error(f"ValueError run_wss_client: {e}")
        return
    except Exception as e:
        logger.error(f"Error run_wss_client: {e}")
    finally:
        logger.info(f"{client_type} stream ended.")

# Get the OHLCV 1 min bars for the given symbol
async def bar_data_handler(data):
    logger.info(f'BAR_1MIN: {bar_to_oneline_string(data)}')
    add_bar_row_to_db(data)

async def updatebar_data_handler(data):
    logger.info(f'UPDATE_BAR: {bar_to_oneline_string(data)}')
    update_bar_row_in_db(data)

def start_sub(stocks_to_track=None, asset='stock'):
    """
    Start the WebSocket client and subscribe to the bars for the symbols to track.

    Alpaca provides sandbox urls for testing, but does not explain how to connect to them.
    """
    stock_url = get_wss_url('stock', testing=TESTING)
    crypto_url = get_wss_url('crypto', testing=TESTING)
    
    # if stocks_to_track is None, get the stocks to track from the database.  
    # if asset is crypto, then use get_crypto_to_track() otherwise use get_stocks_to_track()
    if stocks_to_track is None:
        if asset == 'crypto':
            symbols = get_crypto_to_track()
        else:
            symbols = get_stocks_to_track()
    else:
        symbols = stocks_to_track
    
    try:
        if asset == 'stock':
            wss_client = StockDataStream(API_KEY, API_SECRET, url_override=stock_url)
        elif asset == 'crypto':
            wss_client = CryptoDataStream(API_KEY, API_SECRET, url_override=crypto_url)
        else:
            logger.error(f"Unknown asset type: {asset}")
            return None
    except Exception as e:
        logger.error(f"Failed to connect to the data stream: {e}")
        return None
    finally:
        logger.info(f"Connected to the {asset} data stream")

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

async def update_symbols(wss_client, symbols_to_track=()):
    current_stocks_to_track = symbols_to_track

    while True:
        # if is_trading_hours():
        logger.info(f'update_symbols: sleeping for {CHECK_FREQUENCY} secs...')
        await asyncio.sleep(CHECK_FREQUENCY)  # Sleep for 5 minutes
        
        # Check if the symbols to track have changed
        new_stocks_to_track = get_stocks_to_track()        
        if sorted(current_stocks_to_track) != sorted(new_stocks_to_track):
            logger.info(f'update_symbols: Updating stocks to track...now tracking {new_stocks_to_track}')
            old_stocks = set(current_stocks_to_track)
            update_sub(wss_client, new_stocks_to_track, old_stocks)
            current_stocks_to_track = new_stocks_to_track
        else:
            logger.info('update_symbols: No changes to stocks to track')

async def update_crypto_symbols(wss_client, symbols_to_track=()):
    current_crypto_to_track = symbols_to_track

    while True:
        logger.info(f'update_crypto_symbols: sleeping for {CHECK_FREQUENCY} secs...')
        await asyncio.sleep(CHECK_FREQUENCY)  # Sleep for 5 minutes
        new_crypto_to_track = get_crypto_to_track()
        if sorted(current_crypto_to_track) != sorted(new_crypto_to_track):
            logger.info(f'update_crypto_symbols: Updating crypto to track...now tracking {new_crypto_to_track}')
            old_crypto = set(current_crypto_to_track)
            update_sub(wss_client, new_crypto_to_track, old_crypto)
            current_crypto_to_track = new_crypto_to_track
        else:
            logger.info('update_crypto_symbols: No changes to crypto to track')

async def start_stop_stock_stream(wss_client: DataStream, exit_off_hours: bool = True):
    if wss_client is None:
        logger.error("Error: WebSocket client is None. Exiting start_stop_stock_stream.")
        return
    # sleep for 5 seconds to allow the client to start
    await asyncio.sleep(5)

    while True:
        if is_trading_hours():
            # If the client has stopped, start the client
            if not wss_client._running:
                logger.info("Starting the stock stream...")
                asyncio.create_task(asyncio.to_thread(run_wss_client, wss_client, client_type="stock"))
        else:
            # If the client is running, stop the client
            if wss_client._running:
                str_tmp = "temporarily" if not exit_off_hours else ""
                logger.info(f"Trading hours have ended. Closing stock stream connection {str_tmp}...")
                await wss_client.stop_ws()
                if exit_off_hours:
                    break
            else:
                logger.info("Currently outside of trading hours. Stock stream connection is closed.")

        await asyncio.sleep(60)  # Check every minute

async def sub_bars():
    """
    start 4 tasks:
    - start_stop_stock_stream: starts and stops a stock tracking client that is connected to alpaca's websocket
    - update_symbols: updates the symbols to track at a specified interval.
    - run_wss_client: starts a crypto tracking client that is connected to alpaca's websocket
    - update_crypto_symbols: updates the crypto symbols to track at a specified interval.
    """
    stock_symbols = get_stocks_to_track()
    crypto_symbols = get_crypto_to_track()

    # A check for the connection limit exceeded error
    crypto_stream_url = get_wss_url('crypto', testing=TESTING)
    stock_stream_url = get_wss_url('stock', testing=TESTING)
    connection_available = await test_socket(url=crypto_stream_url)
    if connection_available:
        connection_available = await test_socket(url=stock_stream_url)
    if not connection_available:
        logger.error("No connection available. Exiting sub_bars.")
        return
    
    # A stock data stream client
    wss_stock_client = start_sub(stocks_to_track=stock_symbols, asset='stock')

    # A crypto data stream client
    wss_crypto_client = start_sub(stocks_to_track=crypto_symbols, asset='crypto')

    try:
        await asyncio.gather(
            # thread for tracking stock data
            update_symbols(wss_stock_client, symbols_to_track=stock_symbols),
            start_stop_stock_stream(wss_stock_client, exit_off_hours=False),

            # thread for tracking crypto data
            asyncio.to_thread(run_wss_client, wss_crypto_client, client_type="crypto"),
            update_crypto_symbols(wss_crypto_client, symbols_to_track=crypto_symbols)
        )
    except asyncio.CancelledError:
        logger.error("Subscription interrupted")
    except Exception as e:
        logger.error(f"Unknown Error in sub_bars: {e}")
    finally:
        if wss_stock_client is not None:
            logger.info("Stopping stock WebSocket client...")
            wss_stock_client.stop()
        if wss_crypto_client is not None:
            logger.info("Stopping crypto WebSocket client...")
            wss_crypto_client.stop()

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Capture the market data in a database.')
    
    # Add arguments
    parser.add_argument('-v', '--verbosity', help='Set console output verbosity level. 0 None, 1 Errors, 2 Info, 3 Debug', type=int, default=0)
    parser.add_argument('--log-verbosity', help='Set log file verbosity level. Options are "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL". Default is "INFO".', type=str, default="INFO")

    # Parse the arguments
    args = parser.parse_args()

    # Set the logger level based on verbosity
    set_file_log_level(level_str=args.log_verbosity)

    try:
        asyncio.run(sub_bars())
    except KeyboardInterrupt:
        logger.info("Program interrupted")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__== "__main__":
    main()