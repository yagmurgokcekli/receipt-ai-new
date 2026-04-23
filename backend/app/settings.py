from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    # azure blob storage
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str
    # azure document intelligence
    DOCUMENT_INTELLIGENCE_ENDPOINT: str
    DOCUMENT_INTELLIGENCE_API_KEY: str


settings = Settings()  # type:ignore
