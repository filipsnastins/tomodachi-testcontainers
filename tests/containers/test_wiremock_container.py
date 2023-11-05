from pathlib import Path
from typing import Generator

import httpx
import pytest

from tomodachi_testcontainers import WireMockContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="module")
def wiremock_container() -> Generator[WireMockContainer, None, None]:
    mapping_stubs = Path(__file__).parent / "test-wiremock-container" / "mappings"
    mapping_files = Path(__file__).parent / "test-wiremock-container" / "files"
    with WireMockContainer(mapping_stubs, mapping_files, edge_port=get_available_port(), verbose=True) as container:
        yield container


@pytest.mark.asyncio()
async def test_wiremock_container_starts(wiremock_container: WireMockContainer) -> None:
    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
