"""Abstract relational database container."""

import abc
from typing import Any, NamedTuple

import sqlalchemy
from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from .container import DockerContainer


class DatabaseURL(NamedTuple):
    drivername: str
    username: str
    password: str
    host: str
    port: int
    database: str

    def __repr__(self) -> str:
        return self.to_str()

    def to_str(self) -> str:
        return f"{self.drivername}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseContainer(DockerContainer, abc.ABC):
    internal_port: int
    edge_port: int

    drivername: str
    username: str
    password: str
    database: str

    def __init__(self, image: str, internal_port: int, edge_port: int, **kwargs: Any) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port
        self.with_bind_ports(internal_port, edge_port)

    def get_internal_url(self) -> DatabaseURL:
        return DatabaseURL(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.get_container_internal_ip(),
            port=self.internal_port,
            database=self.database,
        )

    def get_external_url(self) -> DatabaseURL:
        return DatabaseURL(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.get_container_host_ip(),
            port=self.edge_port,
            database=self.database,
        )

    def start(self, timeout: float = 20.0) -> "DatabaseContainer":
        super().start()
        wait_for_database_healthcheck(url=self.get_external_url(), timeout=timeout)
        return self


def wait_for_database_healthcheck(url: DatabaseURL, timeout: float = 20.0, interval: float = 0.5) -> None:
    for attempt in Retrying(stop=stop_after_delay(timeout), wait=wait_fixed(interval), reraise=True):
        with attempt:
            engine = sqlalchemy.create_engine(url.to_str())
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1;"))
