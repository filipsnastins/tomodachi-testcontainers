import tomodachi
from aiohttp import web

from .credit_check import CreditCheckUnavailableError, CustomerCreditCheckFailedError
from .services import create_new_order


class Service(tomodachi.Service):
    @tomodachi.http("POST", r"/order/?")
    async def http_create_order(self, request: web.Request) -> web.Response:
        body = await request.json()
        try:
            order = await create_new_order(
                customer_id=body["customer_id"],
                product=body["product"],
            )
            return web.json_response(order.to_dict())
        except CustomerCreditCheckFailedError:
            return web.json_response({"error": "CREDIT_CHECK_FAILED"}, status=400)
        except CreditCheckUnavailableError:
            return web.json_response({"error": "CREDIT_CHECK_UNAVAILABLE"}, status=503)
