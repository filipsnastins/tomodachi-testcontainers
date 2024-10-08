import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest import mock

import httpx
import pytest
import pytest_asyncio
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers import DockerContainer, LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.assertions import assert_datetime_within_range
from tomodachi_testcontainers.async_probes import probe_until
from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def _create_topics_and_queues(localstack_snssqs_tc: SNSSQSTestClient) -> None:
    await localstack_snssqs_tc.subscribe_to(topic="order--created", queue="customer--order-created")


@pytest.fixture(scope="module")
def tomodachi_container(
    testcontainer_image: str, localstack_container: LocalStackContainer, _create_topics_and_queues: None
) -> Generator[DockerContainer, None, None]:
    with (
        TomodachiContainer(testcontainer_image, http_healthcheck_path="/health")
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SNS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_DYNAMODB_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("DYNAMODB_TABLE_NAME", "autotest-customers")
        .with_command("coverage run -m tomodachi run src/customers.py --production")
    ) as container:
        yield container


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio(loop_scope="session")
async def test_customer_not_found(http_client: httpx.AsyncClient) -> None:
    customer_id = uuid.uuid4()
    response = await http_client.get(f"/customer/{customer_id}")

    assert response.status_code == 404
    assert response.json() == {"error": "CUSTOMER_NOT_FOUND"}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_customer(http_client: httpx.AsyncClient) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]

    assert response.status_code == 200
    assert uuid.UUID(customer_id)
    assert body == {
        "customer_id": customer_id,
        "name": "John Doe",
        "orders": [],
        "created_at": mock.ANY,
    }

    response = await http_client.get(f"/customer/{customer_id}")
    body = response.json()

    assert response.status_code == 200
    assert_datetime_within_range(datetime.fromisoformat(body["created_at"]))
    assert body == {
        "customer_id": customer_id,
        "name": "John Doe",
        "orders": [],
        "created_at": mock.ANY,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_register_created_order(http_client: httpx.AsyncClient, localstack_snssqs_tc: SNSSQSTestClient) -> None:
    response = await http_client.post("/customer", json={"name": "John Doe"})
    body = response.json()
    customer_id = body["customer_id"]

    assert response.status_code == 200

    order_ids = ["6c403295-2755-4178-a4f1-e3b698927971", "c8bb390a-71f4-4e8f-8879-c92261b0e18e"]
    for order_id in order_ids:
        await localstack_snssqs_tc.publish(
            topic="order--created",
            data={
                "event_id": str(uuid.uuid4()),
                "order_id": order_id,
                "customer_id": customer_id,
                "products": ["foo", "bar"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            envelope=JsonBase,
        )

    async def _new_orders_associated_with_customer() -> None:
        response = await http_client.get(f"/customer/{customer_id}")
        body = response.json()

        assert response.status_code == 200
        assert_datetime_within_range(datetime.fromisoformat(body["created_at"]))
        assert body == {
            "customer_id": customer_id,
            "name": "John Doe",
            "orders": [
                {"order_id": order_ids[0]},
                {"order_id": order_ids[1]},
            ],
            "created_at": mock.ANY,
        }

    await probe_until(_new_orders_associated_with_customer)
