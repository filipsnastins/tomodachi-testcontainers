import httpx
import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_hello_testcontainers(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}


@pytest.mark.asyncio(loop_scope="session")
async def test_hello_world(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}
