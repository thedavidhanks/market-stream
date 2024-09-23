import os
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv

load_dotenv()

# Your Alpaca API key ID and secret
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")

def live_alpaca_bars(symbols='AAPL'):
    
    # Get the OHLCV 1 min bars for the given symbol
    async def bar_data_handler(data):
        print(data)    
    
    # Subscribe to the live stock data stream
    wss_client = StockDataStream(API_KEY, API_SECRET)
    wss_client.subscribe_bars(bar_data_handler, *symbols)
    wss_client.run()

if __name__== "__main__":

    live_alpaca_bars(('AAPL','GE'))