from functools import lru_cache
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
