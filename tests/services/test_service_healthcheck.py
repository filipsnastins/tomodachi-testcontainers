# --8<-- [start:tomodachi_container]
from typing import Generator

import pytest

from tomodachi_testcontainers import DockerContainer, TomodachiContainer


@pytest.fixture(scope="module")
def tomodachi_container(testcontainer_image: str) -> Generator[DockerContainer, None, None]:
    with TomodachiContainer(testcontainer_image).with_command(
        "coverage run -m tomodachi run src/healthcheck.py --production"
    ) as container:
        yield container


# --8<-- [end:tomodachi_container]

from typing import AsyncGenerator

import httpx
import pytest_asyncio


@pytest_asyncio.fixture(scope="module")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio
async def test_healthcheck_passes(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
