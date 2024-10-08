import uuid

import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.async_probes import probe_until
from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest.mark.usefixtures("tomodachi_container")
@pytest.mark.asyncio(loop_scope="session")
async def test_customer_not_found_for_newly_created_order(localstack_snssqs_tc: SNSSQSTestClient) -> None:
    # Arrange
    customer_id = str(uuid.uuid4())
    order_id = str(uuid.uuid4())

    # Act
    await localstack_snssqs_tc.publish(
        topic="order--created",
        data={"order_id": order_id, "customer_id": customer_id},
        envelope=JsonBase,
    )

    # Assert
    async def _order_created_event_moved_to_dlq() -> dict[str, str]:
        [event] = await localstack_snssqs_tc.receive("customer--order-created--dlq", JsonBase, dict[str, str])
        return event.payload

    event = await probe_until(_order_created_event_moved_to_dlq, stop_after=10.0)
    assert event == {"order_id": order_id, "customer_id": customer_id}
