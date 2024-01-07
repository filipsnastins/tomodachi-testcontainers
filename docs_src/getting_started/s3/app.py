import tomodachi
from aiohttp import web

from .utils import create_s3_client, get_bucket_name


class Service(tomodachi.Service):
    async def _start_service(self) -> None:
        self._s3_client, self._s3_client_exit_stack = await create_s3_client()

    async def _stop_service(self) -> None:
        await self._s3_client_exit_stack.aclose()

    @tomodachi.http("POST", r"/file/?")
    async def save_file(self, request: web.Request) -> web.Response:
        body = await request.json()
        filename = body["filename"]
        content = body["content"]
        await self._s3_client.put_object(Bucket=get_bucket_name(), Key=filename, Body=content)
        return web.json_response({"key": filename})

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        try:
            s3_object = await self._s3_client.get_object(Bucket=get_bucket_name(), Key=key)
            content = await s3_object["Body"].read()
            return web.json_response({"content": content.decode()})
        except self._s3_client.exceptions.NoSuchKey:
            return web.json_response({"error": "File not found"}, status=404)
