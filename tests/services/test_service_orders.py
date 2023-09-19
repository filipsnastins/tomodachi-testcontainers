import re
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Generator, List, cast

import httpx
import pytest
import pytest_asyncio
from docker.models.images import Image as DockerImage
from tomodachi.envelope.json_base import JsonBase
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

from tomodachi_testcontainers.clients import snssqs_client
from tomodachi_testcontainers.containers import MotoContainer, TomodachiContainer
from tomodachi_testcontainers.pytest.assertions import UUID4_PATTERN, assert_datetime_within_range
from tomodachi_testcontainers.pytest.async_probes import probe_until
from tomodachi_testcontainers.utils import get_available_port


@pytest_asyncio.fixture()
async def _create_topics_and_queues(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(
        moto_sns_client,
        moto_sqs_client,
        topic="order--created",
        queue="order--created",
    )


@pytest.fixture()
def service_orders_container(
    tomodachi_image: DockerImage,
    moto_container: MotoContainer,
    _create_topics_and_queues: None,
    _reset_moto_container_on_teardown: None,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=str(tomodachi_image.id), edge_port=get_available_port(), http_healthcheck_path="/health"
        )
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SNS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("AWS_DYNAMODB_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("DYNAMODB_TABLE_NAME", "orders")
        .with_command("tomodachi run src/orders.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture()
async def http_client(service_orders_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_orders_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_order_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/order/foo")

    assert response.status_code == 404
    assert response.json() == {
        "error": "Order not found",
        "_links": {
            "self": {"href": "/order/foo"},
        },
    }


@pytest.mark.asyncio()
async def test_create_order(http_client: httpx.AsyncClient, moto_sqs_client: SQSClient) -> None:
    customer_id = "4752ce1f-d2a8-4bf1-88e7-ca05b9b3d756"
    products: List[str] = ["MINIMALIST-SPOON", "RETRO-LAMPSHADE"]

    response = await http_client.post("/orders", json={"customer_id": customer_id, "products": products})
    body = response.json()
    order_id = body["order_id"]
    get_order_link = body["_links"]["self"]["href"]

    assert response.status_code == 200
    assert re.match(UUID4_PATTERN, order_id)
    assert body == {
        "order_id": order_id,
        "_links": {
            "self": {"href": f"/order/{order_id}"},
        },
    }

    response = await http_client.get(get_order_link)
    body = response.json()

    assert response.status_code == 200
    assert_datetime_within_range(datetime.fromisoformat(body["created_at"]))
    assert body == {
        "order_id": order_id,
        "customer_id": customer_id,
        "products": products,
        "created_at": body["created_at"],
        "_links": {
            "self": {"href": f"/order/{order_id}"},
        },
    }

    async def _order_created_event_emitted() -> Dict[str, Any]:
        [event] = await snssqs_client.receive(moto_sqs_client, "order--created", JsonBase, Dict[str, Any])
        return event

    event = await probe_until(_order_created_event_emitted)
    assert_datetime_within_range(datetime.fromisoformat(event["created_at"]))
    assert event == {
        "event_id": event["event_id"],
        "order_id": order_id,
        "customer_id": customer_id,
        "products": products,
        "created_at": event["created_at"],
    }
