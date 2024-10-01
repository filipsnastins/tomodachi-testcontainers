import uuid
from unittest import mock

import httpx
import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_customer_not_found(http_client: httpx.AsyncClient) -> None:
    customer_id = uuid.uuid4()
    response = await http_client.get(f"/customer/{customer_id}")

    assert response.status_code == 404
    assert response.json() == {"error": "CUSTOMER_NOT_FOUND"}


@pytest.mark.asyncio(loop_scope="session")
async def test_created_and_get_customer(http_client: httpx.AsyncClient) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]
    assert response.status_code == 200
    assert body == {
        "customer_id": mock.ANY,
        "name": "John Doe",
        "orders": [],
    }

    response = await http_client.get(f"/customer/{customer_id}")
    assert response.status_code == 200
    assert response.json() == {
        "customer_id": customer_id,
        "name": "John Doe",
        "orders": [],
    }
