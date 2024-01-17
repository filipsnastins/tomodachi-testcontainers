import json
import urllib.parse
from datetime import datetime, timezone

import structlog
import tomodachi
from aiohttp import web
from tomodachi.envelope.json_base import JsonBase

from .adapters import aws, s3
from .adapters.tomodachi import create_tomodachi_options
from .utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Service(tomodachi.Service):
    name = "service-s3"

    options = create_tomodachi_options()

    async def _start_service(self) -> None:
        configure_logger()
        self._s3_client, self._s3_client_exit_stack = await aws.create_s3_client()
        self._sns_client, self._sns_client_exit_stack = await aws.create_sns_client()
        await s3.create_s3_bucket(self._s3_client, self._sns_client)

    async def _stop_service(self) -> None:
        await self._s3_client_exit_stack.aclose()
        await self._sns_client_exit_stack.aclose()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        bucket = s3.get_bucket_name()
        log = logger.bind(bucket=bucket, key=key)
        try:
            s3_object = await self._s3_client.get_object(Bucket=bucket, Key=key)
            content = await s3_object["Body"].read()
        except self._s3_client.exceptions.NoSuchKey:
            log.error("file_not_found")
            return web.json_response({"error": "FILE_NOT_FOUND"}, status=404)
        else:
            log.info("file_read")
            return web.json_response({"content": content.decode()})

    @tomodachi.aws_sns_sqs(
        "s3--upload-notification",
        queue_name="s3--upload-notification",
        message_envelope=None,
    )
    async def handle_upload_notification(self, data: str) -> None:
        s3_notification = json.loads(data)
        record = s3_notification["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]
        object_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        etag = record["s3"]["object"]["eTag"]
        request_id = record["responseElements"]["x-amz-id-2"]
        event_time = datetime.strptime(record["eventTime"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

        notification = {
            "uri": f"s3://{bucket_name}/{object_key}",
            "eTag": etag,
            "request_id": request_id,
            "event_time": event_time.isoformat(),
        }
        await tomodachi.aws_sns_sqs_publish(
            self,
            notification,
            topic="s3--file-uploaded",
            message_envelope=JsonBase,
        )
        logger.info("file_uploaded_notification_sent", notification=notification)
