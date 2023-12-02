from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("psycopg.pool").setLevel(logging.INFO)


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings():
    # arguments automatically loaded from .env
    return Settings() # type: ignore 
