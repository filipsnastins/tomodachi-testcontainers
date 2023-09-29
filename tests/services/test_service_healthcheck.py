from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio
from docker.models.images import Image as DockerImage

from tomodachi_testcontainers.containers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def service_healthcheck_container(tomodachi_image: DockerImage) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=str(tomodachi_image.id),
        edge_port=get_available_port(),
    ).with_command("tomodachi run src/healthcheck.py --production") as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture()
async def http_client(service_healthcheck_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_healthcheck_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_healthcheck_passes(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
