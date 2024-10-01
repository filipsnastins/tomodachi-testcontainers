# --8<-- [start:test_order_created_when_credit_check_passed]
from unittest import mock

import httpx
import pytest
import wiremock.client as wm


@pytest.mark.asyncio(loop_scope="session")
async def test_order_created_when_credit_check_passed(http_client: httpx.AsyncClient) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(
            method=wm.HttpMethods.POST,
            url="/credit-check",
            body_patterns=[{wm.WireMockMatchers.EQUAL_TO_JSON: {"customer_id": "123456"}}],
        ),
        response=wm.MappingResponse(
            status=200,
            json_body={"status": "CREDIT_CHECK_PASSED"},
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)

    response = await http_client.post(
        "/order",
        json={"customer_id": "123456", "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": mock.ANY,
        "customer_id": "123456",
        "product": "MINIMALIST-SPOON",
    }


# --8<-- [end:test_order_created_when_credit_check_passed]


# --8<-- [start:test_order_not_created_when_credit_check_failed]
@pytest.mark.asyncio(loop_scope="session")
async def test_order_not_created_when_credit_check_failed(http_client: httpx.AsyncClient) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(
            method=wm.HttpMethods.POST,
            url="/credit-check",
            body_patterns=[{wm.WireMockMatchers.EQUAL_TO_JSON: {"customer_id": "123456"}}],
        ),
        response=wm.MappingResponse(
            status=200,
            json_body={"status": "CREDIT_CHECK_FAILED"},
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)

    response = await http_client.post(
        "/order",
        json={"customer_id": "123456", "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "CREDIT_CHECK_FAILED"}


# --8<-- [end:test_order_not_created_when_credit_check_failed]


# --8<-- [start:test_order_not_created_when_credit_check_service_unavailable]
@pytest.mark.asyncio(loop_scope="session")
async def test_order_not_created_when_credit_check_service_unavailable(http_client: httpx.AsyncClient) -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(method=wm.HttpMethods.POST, url="/credit-check"),
        response=wm.MappingResponse(
            status=500,
            body="Internal Server Error",
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)

    response = await http_client.post(
        "/order",
        json={"customer_id": "123456", "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 503
    assert response.json() == {"error": "CREDIT_CHECK_UNAVAILABLE"}


# --8<-- [end:test_order_not_created_when_credit_check_service_unavailable]
