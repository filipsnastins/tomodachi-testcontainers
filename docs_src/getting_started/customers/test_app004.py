import httpx
import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.pytest.async_probes import probe_until


@pytest.mark.asyncio()
async def test_register_created_order(http_client: httpx.AsyncClient, localstack_snssqs_tc: SNSSQSTestClient) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    customer_id = response.json()["customer_id"]
    assert response.status_code == 200

    order_ids = ["6c403295-2755-4178-a4f1-e3b698927971", "c8bb390a-71f4-4e8f-8879-c92261b0e18e"]
    for order_id in order_ids:
        await localstack_snssqs_tc.publish(
            topic="order--created",
            data={
                "order_id": order_id,
                "customer_id": customer_id,
            },
            envelope=JsonBase,
        )

    async def _new_order_associated_with_customer() -> None:
        response = await http_client.get(f"/customer/{customer_id}")

        assert response.status_code == 200
        assert response.json() == {
            "customer_id": customer_id,
            "name": "John Doe",
            "orders": [
                {"order_id": order_ids[0]},
                {"order_id": order_ids[1]},
            ],
        }

    await probe_until(_new_order_associated_with_customer)