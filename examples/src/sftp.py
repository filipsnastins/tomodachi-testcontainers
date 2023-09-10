from typing import Union

import asyncssh
import structlog
import tomodachi
from aiohttp import web
from src.adapters import sftp
from utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class TomodachiServiceSFTP(tomodachi.Service):
    name = "service-sftp"

    async def _start_service(self) -> None:
        configure_logger()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        links = {
            "_links": {"self": {"href": f"/file/{key}"}},
        }
        log = logger.bind(key=key)
        async with sftp.get_sftp_client() as sftp_client:
            try:
                f = await sftp_client.open(f"upload/{key}", "r")
                content: Union[str, bytes] = await f.read()
                if isinstance(content, bytes):
                    content = content.decode()
            except asyncssh.sftp.SFTPNoSuchFile:
                log.error("file_not_found")
                return web.json_response({"error": "File not found", **links}, status=404)
            else:
                log.info("file_read")
                return web.json_response({"content": content, **links})
