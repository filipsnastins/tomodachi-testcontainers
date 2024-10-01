import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest.mark.xfail(reason="CustomerCreatedEvent is emitted asynchronously")
@pytest.mark.asyncio(loop_scope="session")
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
    events = await localstack_snssqs_tc.receive("customer--created", JsonBase, dict[str, str])
    assert len(events) == 1
    assert events[0].payload == {
        "customer_id": customer_id,
        "name": "John Doe",
    }
