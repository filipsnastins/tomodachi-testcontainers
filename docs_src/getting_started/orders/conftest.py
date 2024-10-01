from typing import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import DockerContainer, TomodachiContainer, WireMockContainer


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
    wiremock_container: WireMockContainer,
) -> Generator[DockerContainer, None, None]:
    with (
        TomodachiContainer(testcontainer_image)
        .with_env("CREDIT_CHECK_SERVICE_URL", wiremock_container.get_internal_url())
        .with_command("tomodachi run getting_started/orders/app.py --production")
    ) as container:
        yield container


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client
