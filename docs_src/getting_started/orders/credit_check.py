import os

import httpx


class CustomerCreditCheckFailedError(Exception):
    pass


class CreditCheckUnavailableError(Exception):
    pass


async def verify_customer_credit(customer_id: str) -> None:
    async with httpx.AsyncClient(base_url=get_credit_check_service_url()) as client:
        response = await client.post("/credit-check", json={"customer_id": customer_id})

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise CreditCheckUnavailableError from e

        body = response.json()
        if body["status"] != "CREDIT_CHECK_PASSED":
            raise CustomerCreditCheckFailedError(customer_id)


def get_credit_check_service_url() -> str:
    return os.environ["CREDIT_CHECK_SERVICE_URL"]
