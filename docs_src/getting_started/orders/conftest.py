from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import TomodachiContainer, WireMockContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
    wiremock_container: WireMockContainer,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=testcontainer_image,
            edge_port=get_available_port(),
        )
        .with_env("CREDIT_CHECK_SERVICE_URL", wiremock_container.get_internal_url())
        .with_command("tomodachi run getting_started/orders/app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client
