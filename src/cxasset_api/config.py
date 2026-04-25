from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CxAsset API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./cxasset.db"
    library_roots: str = "CXA_Library"
    media_token: str = "dev-token"

    model_config = SettingsConfigDict(
        env_prefix="CXASSET_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
