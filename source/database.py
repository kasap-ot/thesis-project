from os import getenv
from functools import lru_cache
from psycopg_pool import AsyncConnectionPool


def get_connection_string() -> str:
    conn_string = (
        f"user={getenv('DB_USER')}\n"
        f"password={getenv('DB_PASSWORD')}\n"
        f"host={getenv('DB_HOST')}\n"
        f"port={getenv('DB_PORT')}\n"
        f"dbname={getenv('DB_NAME')}"
    )

    print("Using connection string:")
    print(conn_string)

    return conn_string


@lru_cache()
def async_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(conninfo=get_connection_string())
