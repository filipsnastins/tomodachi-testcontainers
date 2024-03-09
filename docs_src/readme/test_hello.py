from typing import Generator

import httpx
import pytest

from tomodachi_testcontainers import DockerContainer, TomodachiContainer


@pytest.fixture(scope="session")
def tomodachi_container(testcontainer_image: str) -> Generator[DockerContainer, None, None]:
    with TomodachiContainer(testcontainer_image).with_command(
        "tomodachi run readme/hello.py --production"
    ) as container:
        yield container


@pytest.mark.asyncio()
async def test_hello_testcontainers(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}
