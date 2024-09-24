import psycopg


def connect_to_db(user, password, url, db_name):
    
    # REFERENCE - https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.connect
    db_connection = psycopg.connect(host=url, port=5434, dbname=db_name, user=user, password=password)

    return db_connection