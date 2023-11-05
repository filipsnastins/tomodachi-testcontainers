import asyncio
from contextlib import closing
from typing import Generator, Iterator, cast

import pytest

from tomodachi_testcontainers import DockerContainer
from tomodachi_testcontainers.utils import get_available_port

pytest_plugins = ["pytester"]


class AlpineContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="alpine:latest")

    def log_message_on_container_start(self) -> str:
        return "Alpine container started"


class HTTPBinContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="kennethreitz/httpbin")
        self.edge_port = get_available_port()
        self.with_bind_ports(80, self.edge_port)

    def log_message_on_container_start(self) -> str:
        return "HTTPBin container started"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    with closing(asyncio.new_event_loop()) as loop:
        yield loop


@pytest.fixture()
def alpine_container() -> Generator[AlpineContainer, None, None]:
    with AlpineContainer().with_command("sleep 10") as container:
        yield cast(AlpineContainer, container)


@pytest.fixture()
def httpbin_container() -> Generator[HTTPBinContainer, None, None]:
    with HTTPBinContainer() as container:
        yield cast(HTTPBinContainer, container)
