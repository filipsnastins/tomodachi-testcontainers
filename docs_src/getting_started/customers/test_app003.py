import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.async_probes import probe_until
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

    # Assert
    async def _customer_created_event_emitted() -> dict[str, str]:
        [event] = await localstack_snssqs_tc.receive("customer--created", JsonBase, dict[str, str])
        return event

    event = await probe_until(_customer_created_event_emitted, probe_interval=0.1, stop_after=3.0)
    assert event == {
        "customer_id": customer_id,
        "name": "John Doe",
    }
