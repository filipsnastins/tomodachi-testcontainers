import httpx
import pytest

from tomodachi_testcontainers.containers import MotoContainer


@pytest.mark.asyncio()
async def test_moto_container_starts(moto_container: MotoContainer) -> None:
    async with httpx.AsyncClient(base_url=moto_container.get_external_url()) as client:
        response = await client.get("/moto-api/data.json")

        assert response.status_code == 200
