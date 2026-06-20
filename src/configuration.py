from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field

from typing import Literal


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    env: Literal["dev", "testing", "prod"] = Field(
        validation_alias="ENV", default="dev"
    )
