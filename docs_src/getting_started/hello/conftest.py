# --8<-- [start:tomodachi_container]
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def tomodachi_container(testcontainers_docker_image: str) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=testcontainers_docker_image,
        edge_port=get_available_port(),
    ).with_command("tomodachi run getting_started/hello/app.py --production") as container:
        yield cast(TomodachiContainer, container)


# --8<-- [end:tomodachi_container]

# --8<-- [start:http_client]
from typing import AsyncGenerator

import httpx
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


# --8<-- [end:http_client]
