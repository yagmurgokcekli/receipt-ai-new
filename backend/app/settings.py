from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # azure blob storage
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str
    # azure document intelligence
    DOCUMENT_INTELLIGENCE_ENDPOINT: str
    DOCUMENT_INTELLIGENCE_API_KEY: str
    # azure openai
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str

    @field_validator("*")
    def is_empty(cls, value, info):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return value

    @field_validator("DOCUMENT_INTELLIGENCE_ENDPOINT", "AZURE_OPENAI_ENDPOINT")
    def is_valid(cls, value, info):
        if not value.startswith("https://"):
            raise ValueError(f"{info.field_name} must start with https://")
        return value


settings = Settings()  # type:ignore
