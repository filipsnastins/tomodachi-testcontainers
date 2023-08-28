import json
import os
import urllib.parse
from datetime import datetime, timezone

import structlog
import tomodachi
from adapters import s3
from aiohttp import web
from tomodachi.envelope.json_base import JsonBase
from utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class TomodachiServiceS3(tomodachi.Service):
    name = "service-s3"

    options = tomodachi.Options(
        aws_endpoint_urls=tomodachi.Options.AWSEndpointURLs(
            sns=os.getenv("AWS_SNS_ENDPOINT_URL"),
            sqs=os.getenv("AWS_SQS_ENDPOINT_URL"),
        ),
        http=tomodachi.Options.HTTP(
            content_type="application/json; charset=utf-8",
        ),
        aws_sns_sqs=tomodachi.Options.AWSSNSSQS(
            region_name=os.environ["AWS_REGION"],
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            topic_prefix=os.getenv("AWS_SNS_TOPIC_PREFIX", ""),
            queue_name_prefix=os.getenv("AWS_SQS_QUEUE_NAME_PREFIX", ""),
        ),
    )

    async def _start_service(self) -> None:
        configure_logger()
        await s3.create_s3_bucket()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        links = {
            "_links": {
                "self": {"href": f"/file/{key}"},
            },
        }
        bucket = s3.get_bucket_name()
        log = logger.bind(bucket=bucket, key=key)
        async with s3.get_s3_client() as s3_client:
            try:
                s3_object = await s3_client.get_object(Bucket=bucket, Key=key)
                content = await s3_object["Body"].read()
            except s3_client.exceptions.NoSuchKey:
                log.error("file_not_found")
                return web.json_response({"error": "File not found", **links}, status=404)
            else:
                log.info("file_read")
                return web.json_response({"content": content.decode(), **links})

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
