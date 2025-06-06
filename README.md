This project gets 1 min bars and real-time data from alpaca and writes them to a database.

# Installation

1. Start the container.
This project utilizes Dev Containers extension for Visual Studio Code.  If you're running VS code start up is as follows.
- Start Docker Desktop
- In VS Code, install Dev Containers extension
- Open this project in VS code
- F1 `Dev Containers: Rebuild Container`
If you're not running VS code, this project runs Python 3.12.  Python module versions are in requirements.txt

2. Create a postgreSQL database

3. Install the TimescaleDB extension

4. Create the tables, views, and refresh policy
   SEE data/db_create.sql

7. Add a .env file to the root directory with the following constants:

```
ALPACA_API_KEY = "Your API"
ALPACA_API_SECRET = "YOUR_API_SECRET"
DB_PWD = "DATABASE_PASSWORD"
DB_URL="DATABASE URL"
DB_USER="DATABASE USER"
DB_NAME="DATABASE NAME"
```

# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.