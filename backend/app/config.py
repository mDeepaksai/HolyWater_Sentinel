from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    database_url: str

    secret_key: str = Field(
        alias="JWT_SECRET_KEY"
    )

    algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM"
    )

    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()