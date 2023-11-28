from .config import get_settings
from functools import lru_cache
from psycopg_pool import AsyncConnectionPool

settings = get_settings()

conn_str = f"                       \
    user={settings.db_user}         \
    password={settings.db_password} \
    host={settings.db_host}         \
    port={settings.db_port}         \
    dbname={settings.db_name}       \
"

@lru_cache()
def get_async_pool():
    return AsyncConnectionPool(conninfo=conn_str)
