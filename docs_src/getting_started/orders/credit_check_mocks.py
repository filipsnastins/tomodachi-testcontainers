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


def customer_credit_check_returns_internal_server_error() -> None:
    mapping = wm.Mapping(
        request=wm.MappingRequest(method=wm.HttpMethods.POST, url="/credit-check"),
        response=wm.MappingResponse(
            status=500,
            body="Internal Server Error",
        ),
    )
    wm.Mappings.create_mapping(mapping=mapping)
