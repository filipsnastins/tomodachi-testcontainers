from pathlib import Path
from typing import Generator, cast

import httpx
import pytest
import wiremock.client as wm

from tomodachi_testcontainers import WireMockContainer


@pytest.fixture(scope="session")
def custom_wiremock_container() -> Generator[WireMockContainer, None, None]:
    mapping_stubs = Path(__file__).parent / "test-wiremock-container" / "mappings"
    mapping_files = Path(__file__).parent / "test-wiremock-container" / "files"
    with WireMockContainer(mapping_stubs=mapping_stubs, mapping_files=mapping_files) as container:
        yield cast(WireMockContainer, container)


@pytest.mark.asyncio()
async def test_custom_wiremock_container_configured_from_mapping_files(
    custom_wiremock_container: WireMockContainer,
) -> None:
    async with httpx.AsyncClient(base_url=custom_wiremock_container.get_external_url()) as client:
        response = await client.get("/test-mapping-files")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from mapping files!"}


@pytest.mark.asyncio()
async def test_wiremock_configured_from_environment_variables(wiremock_container: WireMockContainer) -> None:
    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/test-mapping-files")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from mapping files!"}


@pytest.mark.asyncio()
async def test_wiremock_configured_with_python_wiremock_sdk(
    wiremock_container: WireMockContainer, reset_wiremock_container_on_teardown: None
) -> None:
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


@pytest.mark.asyncio()
async def test_wiremock_stub_mappings_deleted_between_tests_reset_wiremock_container_on_teardown_fixture(
    wiremock_container: WireMockContainer, reset_wiremock_container_on_teardown: None
) -> None:
    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/test-wiremock-sdk")  # URL from previous test

    assert response.status_code == 404
