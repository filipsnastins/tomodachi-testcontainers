import tomodachi
from aiohttp import web

from .utils import get_bucket_name, get_s3_client


class Service(tomodachi.Service):
    @tomodachi.http("POST", r"/file/?")
    async def save_file(self, request: web.Request) -> web.Response:
        body = await request.json()
        filename = body["filename"]
        content = body["content"]

        async with get_s3_client() as client:
            await client.put_object(Bucket=get_bucket_name(), Key=filename, Body=content)
            return web.json_response({"key": filename})

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        async with get_s3_client() as client:
            try:
                s3_object = await client.get_object(Bucket=get_bucket_name(), Key=key)
                content = await s3_object["Body"].read()
                return web.json_response({"content": content.decode()})
            except client.exceptions.NoSuchKey:
                return web.json_response({"error": "File not found"}, status=404)
