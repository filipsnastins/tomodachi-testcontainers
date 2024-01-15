from typing import Generator, cast

import httpx
import pytest

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=testcontainer_image,
        edge_port=get_available_port(),
    ).with_command("tomodachi run readme/hello.py --production") as container:
        yield cast(TomodachiContainer, container)


@pytest.mark.asyncio()
async def test_hello_testcontainers(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}
