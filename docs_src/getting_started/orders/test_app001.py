from unittest import mock

import httpx
import pytest
import wiremock.client as wm


@pytest.mark.asyncio()
async def test_order_created_should_credit_check_pass(http_client: httpx.AsyncClient) -> None:
    customer_id = "123456"
    mapping = wm.Mapping(
        request=wm.MappingRequest(
            method=wm.HttpMethods.POST,
            url="/credit-check",
            body_patterns=[{wm.WireMockMatchers.EQUAL_TO_JSON: {"customer_id": customer_id}}],
        ),
        response=wm.MappingResponse(status=200, json_body={"status": "CREDIT_CHECK_PASSED"}),
    )
    wm.Mappings.create_mapping(mapping=mapping)

    response = await http_client.post(
        "/order",
        json={"customer_id": customer_id, "product": "MINIMALIST-SPOON"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": mock.ANY,
        "customer_id": "123456",
        "product": "MINIMALIST-SPOON",
    }
