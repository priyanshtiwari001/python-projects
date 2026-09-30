from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    sercet_key: SecretStr
    algorithm: str = "HS256"
    expire_token_in_mins: int = 5


setting = Settings()  # type: ignore
