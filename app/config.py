"""Environment configuration with validation (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import Client, create_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = Field(validation_alias="SUPABASE_URL")
    supabase_secret_key: str | None = Field(
        default=None, validation_alias="SUPABASE_SECRET_KEY"
    )
    supabase_service_role_key: str | None = Field(
        default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY"
    )
    supabase_access_token: str | None = Field(
        default=None, validation_alias="SUPABASE_ACCESS_TOKEN"
    )
    supabase_project_ref: str | None = Field(
        default=None, validation_alias="SUPABASE_PROJECT_REF"
    )

    @field_validator("supabase_url")
    @classmethod
    def normalize_supabase_url(cls, value: str) -> str:
        url = value.strip().rstrip("/")
        if not url.startswith("https://") or ".supabase.co" not in url:
            raise ValueError("SUPABASE_URL must look like https://<ref>.supabase.co")
        return url

    @field_validator(
        "supabase_secret_key", "supabase_service_role_key", "supabase_access_token"
    )
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_secret_key_format(self) -> Settings:
        for key_name, key_value in (
            ("SUPABASE_SECRET_KEY", self.supabase_secret_key),
            ("SUPABASE_SERVICE_ROLE_KEY", self.supabase_service_role_key),
        ):
            if key_value is None:
                continue
            if key_value.startswith("sb_secret_") or key_value.startswith("eyJ"):
                continue
            raise ValueError(
                f"{key_name} must be a secret key (sb_secret_...) or legacy service_role JWT (eyJ...)"
            )
        return self

    @property
    def resolved_secret_key(self) -> str:
        key = self.supabase_secret_key or self.supabase_service_role_key
        if not key:
            raise ValueError(
                "Set SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY in .env "
                "(Settings > API Keys)."
            )
        return key

    def resolved_access_token(self) -> str:
        token = self.supabase_access_token
        if not token:
            raise ValueError(
                "SUPABASE_ACCESS_TOKEN is not set. Create one at "
                "https://supabase.com/dashboard/account/tokens (starts with sbp_)."
            )
        if not token.startswith("sbp_"):
            raise ValueError("SUPABASE_ACCESS_TOKEN must start with sbp_")
        return token

    def resolved_project_ref(self) -> str:
        if self.supabase_project_ref:
            return self.supabase_project_ref
        host = urlparse(self.supabase_url).hostname or ""
        if host.endswith(".supabase.co"):
            return host.split(".", 1)[0]
        raise ValueError(
            "Could not derive project ref from SUPABASE_URL. Set SUPABASE_PROJECT_REF."
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def create_supabase_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.resolved_secret_key)


def get_client() -> Client:
    """Create a Supabase client."""
    return create_supabase_client()


def get_supabase_url() -> str:
    return get_settings().supabase_url


def get_supabase_secret_key() -> str:
    return get_settings().resolved_secret_key


def get_supabase_access_token() -> str:
    return get_settings().resolved_access_token()


def get_supabase_project_ref() -> str:
    return get_settings().resolved_project_ref()
