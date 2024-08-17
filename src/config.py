from functools import lru_cache
from psycopg_pool import AsyncConnectionPool
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    db_url: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings():
    return Settings() # type: ignore 


def get_connection_string() -> str:
    settings = get_settings()

    conn_string = f"user={settings.db_user}\n"
    conn_string += f"password={settings.db_password}\n"
    conn_string += f"host={settings.db_host}\n"
    conn_string += f"port={settings.db_port}\n"
    conn_string += f"dbname={settings.db_name}"

    return conn_string


@lru_cache()
def get_async_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(conninfo=get_connection_string())
