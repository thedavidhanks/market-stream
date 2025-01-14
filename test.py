import asyncio
import os
import tracemalloc
from dotenv import load_dotenv
from helpers.database import connect_to_db, print_stock_bars_5min, get_crypto_to_track
from helpers.datastream_helper import start_stream

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
# Database info
DB_PWD = os.getenv("MS_DB_PWD")
DB_URL = os.getenv("MS_DB_URL")
DB_USER = os.getenv("MS_DB_USER")
DB_NAME = os.getenv("MS_DB_NAME")
DB_PORT = os.getenv("MS_DB_PORT")


async def test_data_handler(data):
    print(f'TEST DATA: {data}')

def run_wss_client(wss_client, verbosity=2):
    try:
        if wss_client is None:
            raise ValueError("WebSocket client is None.")
        wss_client.run()
    except ValueError as e:
        if "connection limit exceeded" in str(e):
            if verbosity >= 1:
                print(f"Error: {e}")
            exit(1)
        else:
            if verbosity >= 1:
                print(f"ValueError running wss_client: {e}")
            exit(1)
    except Exception as e:
        if verbosity >= 1:
            print(f"run_wss_client Unexpected error: {e}")
        exit(1)

async def main():
    wss_client = start_stream(test_data_handler, test_data_handler, asset='crypto', verbosity=2)
    if wss_client is None:
        print("Failed to start WebSocket client.")
        return
    
    # run_wss_client(wss_client)
    await asyncio.gather(
        # thread for tracking crypto data
        asyncio.to_thread(run_wss_client, wss_client)
    )

if __name__ == '__main__':
    tracemalloc.start()
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unexpected error in main: {e}")