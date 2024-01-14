import asyncio

import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest.mark.asyncio()
async def test_customer_created_event_emitted(
    http_client: httpx.AsyncClient,
    localstack_snssqs_tc: SNSSQSTestClient,
) -> None:
    # Act
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]
    assert response.status_code == 200

    # Assert
    await asyncio.sleep(1)  # Wait for the message to become visible to consumers

    events = await localstack_snssqs_tc.receive("customer--created", JsonBase, dict[str, str])
    assert len(events) == 1
    assert events[0] == {
        "customer_id": customer_id,
        "name": "John Doe",
    }
