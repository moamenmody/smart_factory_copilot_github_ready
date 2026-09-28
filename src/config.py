# -*- coding: utf-8 -*-
"""
Smart Factory Copilot - Configuration Tier.
Centralized environment loader using 12-Factor principles.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
env_file = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file, override=True)
else:
    load_dotenv()

# Database Connection Settings
MSSQL_SERVER = os.getenv("MSSQL_SERVER", ".")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "PlantTelemetryDB")
MSSQL_DRIVER = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
MSSQL_TRUSTED_CONNECTION = os.getenv("MSSQL_TRUSTED_CONNECTION", "yes")

# AI Engine Settings
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

SQLITE_DB_PATH = os.path.join(PROJECT_ROOT, "data/factory_iot.db")

def get_mssql_connection_string() -> str:
    """Generates standard DSN-less ODBC connection string."""
    return (
        f"DRIVER={{{MSSQL_DRIVER}}};"
        f"SERVER={MSSQL_SERVER};"
        f"DATABASE={MSSQL_DATABASE};"
        f"Trusted_Connection={MSSQL_TRUSTED_CONNECTION};"
    )
