import asyncio
import contextlib
from typing import Generator, Iterator, cast

import pytest

from tomodachi_testcontainers import DockerContainer, WebContainer
from tomodachi_testcontainers.utils import get_available_port

pytest_plugins = ["pytester"]


class AlpineContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="alpine:latest")
        self.with_command("sleep infinity")

    def log_message_on_container_start(self) -> str:
        return "Alpine container started"


class HTTPBinContainer(WebContainer):
    def __init__(self) -> None:
        super().__init__(image="kennethreitz/httpbin", internal_port=80, edge_port=get_available_port())

    def log_message_on_container_start(self) -> str:
        return "HTTPBin container started"


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    with contextlib.closing(asyncio.new_event_loop()) as loop:
        yield loop


@pytest.fixture(scope="session")
def alpine_container() -> Generator[AlpineContainer, None, None]:
    with AlpineContainer() as container:
        yield cast(AlpineContainer, container)


@pytest.fixture(scope="session")
def httpbin_container() -> Generator[HTTPBinContainer, None, None]:
    with HTTPBinContainer() as container:
        yield cast(HTTPBinContainer, container)
