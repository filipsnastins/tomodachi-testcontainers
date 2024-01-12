import uuid

import httpx
import pytest


@pytest.mark.asyncio()
async def test_customer_not_found(http_client: httpx.AsyncClient) -> None:
    customer_id = uuid.uuid4()
    response = await http_client.get(f"/customer/{customer_id}")

    assert response.status_code == 404
    assert response.json() == {"error": "CUSTOMER_NOT_FOUND"}
