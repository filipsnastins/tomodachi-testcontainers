import httpx
import pytest
import wiremock.client as wm

from tomodachi_testcontainers import WireMockContainer


@pytest.mark.asyncio()
async def test_wiremock_configured_from_mapping_files(wiremock_container: WireMockContainer) -> None:
    async with httpx.AsyncClient(base_url=wiremock_container.get_external_url()) as client:
        response = await client.get("/test-mapping-files")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from mapping files!"}


@pytest.mark.asyncio()
async def test_wiremock_configured_with_python_wiremock_sdk(wiremock_container: WireMockContainer) -> None:
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
