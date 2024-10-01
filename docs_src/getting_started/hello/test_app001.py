# --8<-- [start:test_hello_testcontainers]
import httpx
import pytest

from tomodachi_testcontainers import TomodachiContainer


@pytest.mark.asyncio(loop_scope="session")
async def test_hello_testcontainers(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}


# --8<-- [end:test_hello_testcontainers]


# --8<-- [start:test_hello_world]
@pytest.mark.asyncio(loop_scope="session")
async def test_hello_world(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}


# --8<-- [end:test_hello_world]
