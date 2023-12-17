"""PostgreSQL testcontainer.

Adaptation of https://github.com/testcontainers/testcontainers-python/tree/main/postgres
"""
import os
from typing import Any, Optional

from .common import DatabaseContainer


class PostgreSQLContainer(DatabaseContainer):
    def __init__(
        self,
        image: str = "postgres:16",
        internal_port: int = 5432,
        edge_port: int = 5432,
        drivername: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, internal_port=internal_port, edge_port=edge_port, **kwargs)

        self.drivername = drivername or os.getenv("POSTGRES_DRIVERNAME") or "postgresql+psycopg2"
        self.username = username or os.getenv("POSTGRES_USER") or "username"
        self.password = password or os.getenv("POSTGRES_PASSWORD") or "password"
        self.database = database or os.getenv("POSTGRES_DB") or "db"

        self.with_env("POSTGRES_USER", self.username)
        self.with_env("POSTGRES_PASSWORD", self.password)
        self.with_env("POSTGRES_DB", self.database)

        # Do not flush data on disk to improve test container performance
        # https://pythonspeed.com/articles/faster-db-tests/
        self.with_command("-c fsync=off")

    def log_message_on_container_start(self) -> str:
        return f"PostgreSQL started: {self.get_external_url()}"
