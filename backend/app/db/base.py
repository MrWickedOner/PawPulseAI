import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def query_db(sql: str):
    """Execute a SQL statement using the team-db CLI."""
    try:
        result = subprocess.run(
            ["team-db", sql],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return []
    except subprocess.CalledProcessError as e:
        logger.error(f"SQL Error: {e.stderr}")
        raise Exception(f"Database error: {e.stderr}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {result.stdout}")
        return []

def escape_string(s: str) -> str:
    if s is None:
        return "NULL"
    return s.replace("'", "''")
