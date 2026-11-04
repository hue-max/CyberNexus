import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

# Load environment variables from the backend folder
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


def get_connection():
    """Connect to CyberNexusDB using Windows Authentication."""
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_NAME", "CyberNexusDB")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string, timeout=5)