from typing import Dict

import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.pytest.async_probes import probe_until


@pytest.mark.asyncio()
async def test_customer_created_event_emitted(
    http_client: httpx.AsyncClient,
    localstack_snssqs_tc: SNSSQSTestClient,
) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]

    async def _customer_created_event_emitted() -> Dict[str, str]:
        [event] = await localstack_snssqs_tc.receive("customer--created", JsonBase, Dict[str, str])
        return event

    event = await probe_until(_customer_created_event_emitted)
    assert event == {
        "customer_id": customer_id,
        "name": "John Doe",
    }