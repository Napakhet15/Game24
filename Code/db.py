# Panyasiri
import mysql.connector
from mysql.connector import pooling

from config import Config

_pool = None


def get_connection():
    """Return a pooled MySQL connection (lazy init so the app can import
    without a live DB, e.g. during tests)."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="vase_pool",
            pool_size=5,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
        )
    return _pool.get_connection()
