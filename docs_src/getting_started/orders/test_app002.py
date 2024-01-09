# --8<-- [end:mocks]
import wiremock.client as wm


def customer_credit_check_passes(customer_id: str) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(
            method=wm.HttpMethods.POST,
            url="/credit-check",
            body_patterns=[{wm.WireMockMatchers.EQUAL_TO_JSON: {"customer_id": customer_id}}],
        ),
        response=wm.MappingResponse(
            status=200,
            json_body={"status": "CREDIT_CHECK_PASSED"},
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)


def customer_credit_check_fails(customer_id: str) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(
            method=wm.HttpMethods.POST,
            url="/credit-check",
            body_patterns=[{wm.WireMockMatchers.EQUAL_TO_JSON: {"customer_id": customer_id}}],
        ),
        response=wm.MappingResponse(
            status=200,
            json_body={"status": "CREDIT_CHECK_FAILED"},
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)


# --8<-- [end:mocks]


# --8<-- [start:tests]
from unittest import mock

import httpx
import pytest


@pytest.mark.asyncio()
async def test_order_created_when_credit_check_passed(http_client: httpx.AsyncClient) -> None:
    customer_id = "123456"
    customer_credit_check_passes(customer_id)

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
    customer_credit_check_fails(customer_id)

    response = await http_client.post(
        "/order",
        json={"customer_id": customer_id, "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "CREDIT_CHECK_FAILED"}


# --8<-- [end:tests]
