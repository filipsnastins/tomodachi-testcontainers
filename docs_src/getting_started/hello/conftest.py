# --8<-- [start:tomodachi_container]
from typing import Generator

import pytest

from tomodachi_testcontainers import DockerContainer, TomodachiContainer


@pytest.fixture(scope="session")
def tomodachi_container(testcontainer_image: str) -> Generator[DockerContainer, None, None]:
    with TomodachiContainer(testcontainer_image).with_command(
        "tomodachi run getting_started/hello/app.py --production"
    ) as container:
        yield container


# --8<-- [end:tomodachi_container]

# --8<-- [start:http_client]
from typing import AsyncGenerator

import httpx
import pytest_asyncio


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


# --8<-- [end:http_client]
