from functools import lru_cache
from pathlib import Path
import secrets

from pydantic import PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SentinelTrace"
    version: str = "0.1.0"
    database_url: str = "sqlite:///./sentineltrace.db"
    max_upload_bytes: int = 10 * 1024 * 1024
    cors_origins: str = "http://localhost:5173"
    auth_secret: str = ""
    auth_token_ttl_minutes: int = 480
    login_rate_limit: int = 10
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    _runtime_secret: str = PrivateAttr(default_factory=lambda: secrets.token_urlsafe(32))

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]

    @property
    def auth_secret_runtime(self) -> str:
        return self.auth_secret or self._runtime_secret


@lru_cache
def get_settings() -> Settings:
    return Settings()


BASE_DIR = Path(__file__).resolve().parents[2]
