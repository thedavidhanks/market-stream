import os
import json
import websockets
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca.data.live.websocket import DataStream
from alpaca.common.enums import BaseURL
from alpaca.data.enums import DataFeed, CryptoFeed

from helpers.database import get_stocks_to_track, get_crypto_to_track
from helpers.logger import logger

load_dotenv()

# Alpaca API key ID and secret
API_KEY = os.getenv("MS_ALPACA_API_KEY")
API_SECRET = os.getenv("MS_ALPACA_API_SECRET")
TESTING = False


def get_wss_url(asset='stock', testing: bool = TESTING) -> str:
    """
    Get the WebSocket URL for the asset.

    Alpaca provides sandbox urls for testing, but does not explain how to connect to them.
    https://docs.alpaca.markets/docs/streaming-market-data#connection
    https://docs.alpaca.markets/docs/real-time-stock-pricing-data
    https://docs.alpaca.markets/docs/real-time-crypto-pricing-data

    Inputs:
    - asset (str): The asset to track, either 'stock' or 'crypto'.
    - testing (bool): Whether to use the sandbox url for testing.

    Returns:
    - str: The WebSocket URL for the asset.
    """
    baseURL = BaseURL.MARKET_DATA_STREAM.value if not testing else "wss://stream.data.sandbox.alpaca.markets"
    if asset == 'stock':
        return baseURL + "/v2/" + DataFeed.IEX.value
    elif asset == 'crypto':
        return baseURL+"/v1beta3/crypto/"+CryptoFeed.US.value
    else:
        return None
    
def start_stream(bar_data_handler, updatebar_data_handler, stocks_to_track = None, asset='stock') -> DataStream:
    """
    Start the WebSocket client and subscribe to the bars for the symbols to track.
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
    except Exception as e:
        logger.warning(f"Failed to connect to the data stream: {e}")
        return None
    else:
        logger.info(f"Connected to the {asset} data stream")

    wss_client.subscribe_bars(bar_data_handler, *symbols)
    wss_client.subscribe_updated_bars(updatebar_data_handler, *symbols)
    
    return wss_client

async def test_socket(url = "wss://stream.data.sandbox.alpaca.markets/v1beta3/crypto/us") -> bool:
    """
    Test the connection to the WebSocket client.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({'action': 'auth', 'key': API_KEY, 'secret': API_SECRET}))
        response = await ws.recv()
        logger.debug(f"Response: {response}")
        # if the response is successful, then listen to the stream
        if json.loads(response)[0]["T"] == 'success':
            await ws.send(json.dumps({'action': 'subscribe', 'bars': ["XTZ/USD"] }))
            response = await ws.recv()
            logger.debug(f"Response: {response}")
            response_dict = json.loads(response)[0]
            if response_dict["T"] == 'success':
                return True
            else:
                logger.warning(f"Failed to subscribe to the stream: {response_dict['msg']}")
                return False
        else:
            return False
        


if __name__== "__main__":
    async def test_data_handler(data):
        logger.info(f'TEST DATA: {data}')

    wss_client = start_stream(test_data_handler, test_data_handler, asset='crypto')