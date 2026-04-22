import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = f"{pathlib.Path(__file__).resolve().parent.parent}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"{ROOT_DIR}/.env")

    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str


settings = Settings()  # type:ignore
