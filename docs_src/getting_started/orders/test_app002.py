from unittest import mock

import httpx
import pytest

from . import credit_check_mocks

pytestmark = pytest.mark.usefixtures("reset_wiremock_container_on_teardown")


@pytest.mark.asyncio()
async def test_order_created_when_credit_check_passed(http_client: httpx.AsyncClient) -> None:
    customer_id = "123456"
    credit_check_mocks.customer_credit_check_passes(customer_id)

    response = await http_client.post(
        "/order",
        json={"customer_id": customer_id, "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": mock.ANY,
        "customer_id": customer_id,
        "product": "MINIMALIST-SPOON",
    }


@pytest.mark.asyncio()
async def test_order_not_created_when_credit_check_failed(http_client: httpx.AsyncClient) -> None:
    customer_id = "123456"
    credit_check_mocks.customer_credit_check_fails(customer_id)

    response = await http_client.post(
        "/order",
        json={"customer_id": customer_id, "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "CREDIT_CHECK_FAILED"}


@pytest.mark.asyncio()
async def test_order_not_created_when_credit_check_service_unavailable(http_client: httpx.AsyncClient) -> None:
    credit_check_mocks.customer_credit_check_returns_internal_server_error()

    response = await http_client.post(
        "/order",
        json={"customer_id": "123456", "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 503
    assert response.json() == {"error": "CREDIT_CHECK_UNAVAILABLE"}
