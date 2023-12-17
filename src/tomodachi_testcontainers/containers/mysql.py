"""MySQL testcontainer.

Adaptation of https://github.com/testcontainers/testcontainers-python/tree/main/mysql
"""
import os
from typing import Any, Optional

from .common import DatabaseContainer


class MySQLContainer(DatabaseContainer):
    def __init__(
        self,
        image: str = "mysql:8",
        internal_port: int = 3306,
        edge_port: int = 3306,
        drivername: Optional[str] = None,
        username: Optional[str] = None,
        root_password: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, internal_port=internal_port, edge_port=edge_port, **kwargs)

        self.drivername = drivername or os.getenv("MYSQL_DRIVERNAME") or "mysql+pymysql"
        self.username = username or os.getenv("MYSQL_USER") or "username"
        self.root_password = root_password or os.getenv("MYSQL_ROOT_PASSWORD") or "root"
        self.password = password or os.getenv("MYSQL_PASSWORD") or "password"
        self.database = database or os.getenv("MYSQL_DATABASE") or "db"

        if self.username == "root":
            self.root_password = self.password

        self.with_env("MYSQL_USER", self.username)
        self.with_env("MYSQL_ROOT_PASSWORD", self.root_password)
        self.with_env("MYSQL_PASSWORD", self.password)
        self.with_env("MYSQL_DATABASE", self.database)

        # Do not flush data on disk to improve test container performance
        # https://pythonspeed.com/articles/faster-db-tests/
        self.with_command("--innodb_flush_method=O_DIRECT_NO_FSYNC")

    def log_message_on_container_start(self) -> str:
        return f"MySQL started: {self.get_external_url()}"
