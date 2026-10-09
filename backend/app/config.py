from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DealRoom Security"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./dealroom.db"
    frontend_url: str = "http://localhost:5173"
    frontend_origin_regex: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_url.split(",") if o.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        return self.frontend_origin_regex or None

    class Config:
        env_file = ".env"


settings = Settings()
