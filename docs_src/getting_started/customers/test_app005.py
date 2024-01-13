import uuid
from typing import Dict

import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.pytest.async_probes import probe_until


@pytest.mark.usefixtures("tomodachi_container")
@pytest.mark.asyncio()
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
    async def _order_created_event_moved_to_dlq() -> Dict[str, str]:
        [event] = await localstack_snssqs_tc.receive("customer--order-created--dlq", JsonBase, Dict[str, str])
        return event

    event = await probe_until(_order_created_event_moved_to_dlq, stop_after=10.0)
    assert event == {"order_id": order_id, "customer_id": customer_id}
