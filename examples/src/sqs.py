import structlog
import tomodachi
from aiohttp import web
from tomodachi.envelope.json_base import JsonBase

from .adapters.tomodachi import create_tomodachi_options
from .utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Service(tomodachi.Service):
    name = "service-sqs"

    options = create_tomodachi_options()

    async def _start_service(self) -> None:
        configure_logger()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    @tomodachi.aws_sns_sqs(
        queue_name="test-queue",
        message_envelope=JsonBase,
    )
    async def receive_message_from_test_queue(self, data: dict) -> None:
        logger.info("message_received", data=data)
