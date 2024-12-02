import asyncio
import os
from dotenv import load_dotenv
from helpers.database import get_stocks_to_track
from alpaca.data.live import StockDataStream, CryptoDataStream

from helpers.database import get_stocks_to_track

load_dotenv()

# # Alpaca API key ID and secret
API_KEY = os.getenv("MS_ALPACA_API_KEY")
API_SECRET = os.getenv("MS_ALPACA_API_SECRET")
TESTING = False
TRACKING = 'stocks'

CHECK_FREQUENCY = 60  # 5 minutes

async def bar_data_handler(data):
    print(data)

def update_sub(client, new_symbols, old_symbols):
    client.unsubscribe_bars(*old_symbols)
    client.subscribe_bars(bar_data_handler, *new_symbols)

async def update_symbols(wss_client, verbosity=0):
    current_stocks_to_track = ()

    while True:
        if verbosity >=2:
            print(f'Checking for updates to stocks to track in {CHECK_FREQUENCY} secs...')
        await asyncio.sleep(CHECK_FREQUENCY)  # Sleep for 5 minutes
        new_stocks_to_track = get_stocks_to_track()
        if sorted(current_stocks_to_track) != sorted(new_stocks_to_track):
            if verbosity >=2:
                print(f'Updating stocks to track...now tracking {new_stocks_to_track}')
            old_stocks = set(current_stocks_to_track)
            update_sub(wss_client, new_stocks_to_track, old_stocks)
            current_stocks_to_track = new_stocks_to_track
        else:
            if verbosity >=2:
                print('No changes to stocks to track')
        

def start_sub():
    stock_symbols = get_stocks_to_track()
    crypto_symbols = ('BTC','ETH','LTC')
    symbols = stock_symbols if TRACKING == 'stocks' else crypto_symbols
    stock_url = "wss://stream.data.sandbox.alpaca.markets/v2/iex" if TESTING else None
    crypto_url = "wss://stream.data.sandbox.alpaca.markets/v1beta3/crypto/us" if TESTING else None
    
    print(f'Setting up DataStream with the following\n\tTesting: {TESTING}\n\tTracking: {TRACKING}')
    try:
        wss_client = StockDataStream(API_KEY, API_SECRET, url_override=stock_url) if TRACKING == 'stocks' else CryptoDataStream(API_KEY, API_SECRET, url_override=crypto_url)
    except Exception as e:
        print(f"Failed to connect to the data stream: {e}")
        exit(1)
    
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    return wss_client

async def sub_bars():
    wss_client = start_sub()

    try:
        await asyncio.gather(
            asyncio.to_thread(run_wss_client, wss_client),
            update_symbols(wss_client, verbosity=2)
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
        wss_client.stop()

def run_wss_client(wss_client):
    try:
        wss_client.run()
    except ValueError as e:
        if "connection limit exceeded" in str(e):
            print(f"ValueError (connection limit) running wss_client: {e}")
            os._exit(1)
        else:
            print(f"ValueError running wss_client: {e}")
            raise
    except Exception as e:
        print(f"Error running wss_client: {e}")
        os._exit(1)

def main():
    try:
        asyncio.run(sub_bars())
    except KeyboardInterrupt:
        print("Program interrupted")


if __name__ == "__main__":
    main()