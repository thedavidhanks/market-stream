
"""
Utilize the following curl command and download all of alpaca crypto data.

curl --request GET 'https://api.alpaca.markets/v2/assets?asset_class=crypto' \
--header 'Apca-Api-Key-Id: <KEY>' \
--header 'Apca-Api-Secret-Key: <SECRET>'

return a dictionary of the data
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_crypto_data():
    url = 'https://paper-api.alpaca.markets/v2/assets?asset_class=crypto'
    # Alpaca API key ID and secret
    API_KEY = os.getenv("MS_ALPACA_API_KEY")
    API_SECRET = os.getenv("MS_ALPACA_API_SECRET")

    headers = {
        'Apca-Api-Key-Id': API_KEY,
        'Apca-Api-Secret-Key': API_SECRET
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    if 'message' in data:
        raise Exception(data['message'])
    return data

def get_crypto_symbols():
    try:
        data = get_crypto_data()
    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return None
    symbols = [crypto['symbol'] for crypto in data]
    return symbols

def get_crypto_symbols_and_names():
    data = get_crypto_data()
    try:
        data = get_crypto_data()
    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return None
    symbols_and_names = {crypto['symbol']:crypto['name'] for crypto in data}
    return symbols_and_names


if __name__ == '__main__':
    # print(get_crypto_data())
    print(get_crypto_symbols())
    # print(get_crypto_symbols_and_names())
