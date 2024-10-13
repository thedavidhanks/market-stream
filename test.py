import os
from dotenv import load_dotenv
from helpers.database import connect_to_db, print_stock_bars_5min

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

connection = connect_to_db(DB_USER, DB_PWD, DB_URL, DB_NAME, port=DB_PORT)

print_stock_bars_5min(connection)