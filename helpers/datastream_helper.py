import os
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca.data.live.websocket import DataStream

from helpers.database import get_stocks_to_track, get_crypto_to_track

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("MS_ALPACA_API_KEY")
API_SECRET = os.getenv("MS_ALPACA_API_SECRET")
TESTING = False

def start_stream(bar_data_handler, updatebar_data_handler, stocks_to_track = None, asset='stock', verbosity=0) -> DataStream:
    """
    Start the WebSocket client and subscribe to the bars for the symbols to track.

    Alpaca provides sandbox urls for testing, but does not explain how to connect to them.
    """
    stock_url = "wss://stream.data.sandbox.alpaca.markets/v2/iex" if TESTING else None
    crypto_url = "wss://stream.data.sandbox.alpaca.markets/v1beta3/crypto/us" if TESTING else None
    
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
    except Exception as e:
        if verbosity >=1: print(f"Failed to connect to the data stream: {e}")
        return None
    else:
        if verbosity >=2: print(f"Connected to the {asset} data stream")
    
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    wss_client.subscribe_updated_bars(updatebar_data_handler, *symbols)
    
    return wss_client

if __name__== "__main__":
    async def test_data_handler(data):
        print(f'TEST DATA: {data}')
    
    wss_client = start_stream(test_data_handler, test_data_handler, asset='crypto', verbosity=2)