from pathlib import Path
from typing import Generator, cast

import httpx
import pytest
import wiremock.client as wm
from wiremock.constants import Config as WireMockConfig

from tomodachi_testcontainers import WireMockContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="module")
def wiremock_container() -> Generator[WireMockContainer, None, None]:
    mapping_stubs = Path(__file__).parent / "test-wiremock-container" / "mappings"
    mapping_files = Path(__file__).parent / "test-wiremock-container" / "files"
    with WireMockContainer(mapping_stubs, mapping_files, edge_port=get_available_port(), verbose=True) as container:
        container = cast(WireMockContainer, container)
        WireMockConfig.base_url = f"{container.get_external_url()}/__admin/"  # WireMock SDK is optional
        yield container


@pytest.mark.asyncio()
async def test_wiremock_configured_from_mapping_files(wiremock_container: WireMockContainer) -> None:
    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/test-mapping-files")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from mapping files!"}


@pytest.mark.asyncio()
async def test_wiremock_configured_with_sdk(wiremock_container: WireMockContainer) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(method=wm.HttpMethods.GET, url="/test-wiremock-sdk"),
        response=wm.MappingResponse(status=200, json_body={"message": "Mapping created by WireMock SDK!"}),
        persistent=False,
    )
    wm.Mappings.create_mapping(mapping=mapping)

    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/test-wiremock-sdk")

    assert response.status_code == 200
    assert response.json() == {"message": "Mapping created by WireMock SDK!"}
