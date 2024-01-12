import asyncio
from typing import Dict

import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest.mark.asyncio()
async def test_customer_created_event_emitted(
    http_client: httpx.AsyncClient,
    localstack_snssqs_tc: SNSSQSTestClient,
) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]
    assert response.status_code == 200

    await asyncio.sleep(1)  # Wait for the event to be emitted

    events = await localstack_snssqs_tc.receive("customer--created", JsonBase, Dict[str, str])
    assert len(events) == 1
    assert events[0] == {
        "customer_id": customer_id,
        "name": "John Doe",
    }
