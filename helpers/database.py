import os
import psycopg

from dotenv import load_dotenv

load_dotenv()
DB_PWD = os.getenv("DB_PWD")
DB_URL = os.getenv("DB_URL")
DB_USER = os.getenv("DB_USER")

# REFERENCE - https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
db_connection = psycopg.connect(host=DB_URL, port=5434, dbname="postgres", user=DB_USER, password=DB_PWD)

print(db_connection.info.status)