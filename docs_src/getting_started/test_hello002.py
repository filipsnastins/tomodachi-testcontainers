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
    ).with_command("tomodachi run getting_started/hello.py --production") as container:
        yield cast(TomodachiContainer, container)


# --8<-- [end:tomodachi_container]


# --8<-- [start:tests]
from typing import AsyncGenerator

import httpx
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_hello_testcontainers(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}


@pytest.mark.asyncio()
async def test_hello_world(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}


# --8<-- [end:tests]
