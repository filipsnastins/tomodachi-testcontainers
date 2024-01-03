import tomodachi
from aiohttp import web


class Service(tomodachi.Service):
    @tomodachi.http("GET", r"/hello/?")
    async def hello(self, request: web.Request) -> web.Response:
        name = request.query.get("name", "World")
        return web.json_response(data={"message": f"Hello, {name}!"})
