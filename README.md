This project gets 1 min bars and real-time data from alpaca and writes them to a database.

# Installation

1. Start the container.
This project utilizes Dev Containers extension for Visual Studio Code.  If you're running VS code start up is as follows.
- Start Docker Desktop
- In VS Code, install Dev Containers extension
- Open this project in VS code
- F1 `Dev Containers: Rebuild Container`
If you're not running VS code, this project runs Python 3.12.  Python module versions are in requirements.txt

2. Create a postgreSQL server


3. Install the TimescaleDB extension

4. Create the tables, views, and refresh policy
   - Create the database
   ```
   CREATE DATABASE mlmarketdata;
   \c mlmarketdata
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```
   - in psql run the following files:  
      -  ./data/db_create.sql
      -  ./data/db_create2.sql
      -  ./data/db_create3.sql

7. Add a .env file to the root directory with the following constants:

```
MS_ALPACA_API_KEY = "Your API"
MS_ALPACA_API_SECRET = "YOUR_API_SECRET"
MS_DB_PWD = "DATABASE_PASSWORD"
MS_DB_URL="DATABASE URL"
MS_DB_PORT=5432
MS_DB_USER="DATABASE USER"
MS_DB_NAME="DATABASE NAME"
```

# Run

Run the program using the following command:   

`$ python main.py`

## Help info
To view other arguments a --help argument is available.

```
$ python main.py --help

usage: main.py [-h] [-v VERBOSITY]

Capture the market data in a database.

options:
  -h, --help            show this help message and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        Set output verbosity level. 0 None, 1 Errors, 2 Info, 3 Debug
```
# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.