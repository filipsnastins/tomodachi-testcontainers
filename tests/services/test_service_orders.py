import re
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Generator, List, cast
from unittest import mock

import httpx
import pytest
import pytest_asyncio
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers import MotoContainer, TomodachiContainer
from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.pytest.assertions import UUID4_PATTERN, assert_datetime_within_range
from tomodachi_testcontainers.pytest.async_probes import probe_until
from tomodachi_testcontainers.utils import get_available_port


@pytest_asyncio.fixture(scope="module")
async def _create_topics_and_queues(moto_snssqs_tc: SNSSQSTestClient) -> None:
    await moto_snssqs_tc.subscribe_to(topic="order--created", queue="order--created")


@pytest.fixture(scope="module")
def tomodachi_container(
    testcontainer_image: str, moto_container: MotoContainer, _create_topics_and_queues: None
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=testcontainer_image,
            edge_port=get_available_port(),
            http_healthcheck_path="/health",
        )
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SNS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("AWS_DYNAMODB_ENDPOINT_URL", moto_container.get_internal_url())
        .with_env("DYNAMODB_TABLE_NAME", "autotest-orders")
        .with_command("coverage run -m tomodachi run src/orders.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)
    moto_container.reset_moto()


@pytest_asyncio.fixture(scope="module")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_order_not_found(http_client: httpx.AsyncClient) -> None:
    order_id = str(uuid.uuid4())
    response = await http_client.get(f"/order/{order_id}")

    assert response.status_code == 404
    assert response.json() == {"error": "ORDER_NOT_FOUND"}


@pytest.mark.asyncio()
async def test_create_order(http_client: httpx.AsyncClient, moto_snssqs_tc: SNSSQSTestClient) -> None:
    customer_id = str(uuid.uuid4())
    products: List[str] = ["MINIMALIST-SPOON", "RETRO-LAMPSHADE"]

    response = await http_client.post("/order", json={"customer_id": customer_id, "products": products})
    body = response.json()
    order_id = body["order_id"]

    assert response.status_code == 200
    assert re.match(UUID4_PATTERN, order_id)
    assert body == {"order_id": order_id, "customer_id": customer_id, "products": products, "created_at": mock.ANY}

    response = await http_client.get(f"/order/{order_id}")
    body = response.json()

    assert response.status_code == 200
    assert_datetime_within_range(datetime.fromisoformat(body["created_at"]))
    assert body == {
        "order_id": order_id,
        "customer_id": customer_id,
        "products": products,
        "created_at": mock.ANY,
    }

    async def _order_created_event_emitted() -> Dict[str, Any]:
        [event] = await moto_snssqs_tc.receive("order--created", JsonBase, Dict[str, Any])
        return event

    event = await probe_until(_order_created_event_emitted)
    assert_datetime_within_range(datetime.fromisoformat(event["created_at"]))
    assert event == {
        "event_id": event["event_id"],
        "order_id": order_id,
        "customer_id": customer_id,
        "products": products,
        "created_at": mock.ANY,
    }
