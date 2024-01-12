import tomodachi
from aiohttp import web


class Service(tomodachi.Service):
    name = "service-healthcheck"

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})
