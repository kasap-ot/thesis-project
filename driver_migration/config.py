from functools import lru_cache

from pydantic import BaseSettings

# uncomment to see psycopg.pool logs
# import logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# logging.getLogger("psycopg.pool").setLevel(logging.INFO)


class Settings(BaseSettings):
    db_user: str = "diplomska-user"
    db_password: str = "diplomska-password"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "diplomska-db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
