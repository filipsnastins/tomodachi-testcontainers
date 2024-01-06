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


# --8<-- [start:test_hello_testcontainers]
import httpx


@pytest.mark.asyncio()
async def test_hello_testcontainers(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}


# --8<-- [end:test_hello_testcontainers]


# --8<-- [start:test_hello_world]


@pytest.mark.asyncio()
async def test_hello_world(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}


# --8<-- [end:test_hello_world]
