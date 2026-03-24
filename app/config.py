import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def get_env_variable()-> dict:
    """Get an environment variable or return a default value."""
    return {
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "database": os.environ.get("DB_NAME", "sports_calendar"),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "port": int(os.environ.get("DB_PORT", 3306))
    }
