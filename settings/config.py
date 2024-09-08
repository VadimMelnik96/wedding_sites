from typing import Sequence, Self

from dotenv import load_dotenv
from pydantic import SecretStr, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PostgresConfig(EnvBaseSettings):
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    pool_size: int = 10
    pool_overflow_size: int = 10
    leader_usage_coefficient: float = 0.3
    echo: bool = False
    autoflush: bool = False
    autocommit: bool = False
    expire_on_commit: bool = False
    engine_health_check_delay: int = 1
    dsn: PostgresDsn | None = None
    slave_hosts: Sequence[str] | str = ""
    slave_dsns: Sequence[PostgresDsn] | str = ""

    @model_validator(mode="after")
    def assemble_db_connection(self) -> Self:
        if self.dsn is None:
            self.dsn = PostgresDsn.build(
                scheme=self.scheme,
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=f"{self.db}",
            )
        return self

    @classmethod
    def assemble_slave_hosts(cls, v: str) -> list[str]:
        if v == "":
            return []
        return [item.strip() for item in v.split(",")]

    @model_validator(mode="after")
    def assemble_slave_dsns(self) -> Self:
        if self.slave_dsns is not None:
            return self
        dsns: list[PostgresDsn] = []
        for host in self.slave_hosts:
            dsns.append(
                PostgresDsn.build(
                    scheme=self.scheme,
                    username=self.user,
                    password=self.password,
                    host=host,
                    port=self.port,
                    path=f"{self.db}",
                )
            )
        self.slave_dsns = dsns
        return self

    model_config = SettingsConfigDict(env_prefix="postgres_")


class BotSettings(EnvBaseSettings):

    token: SecretStr

    model_config = SettingsConfigDict(env_prefix="bot_")


class Settings(EnvBaseSettings):

    bot: BotSettings = BotSettings()
    database: PostgresConfig = PostgresConfig()


config = Settings()
