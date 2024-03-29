import os

import structlog
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


def get_bucket_name() -> str:
    return os.environ["AWS_S3_BUCKET_NAME"]


def get_s3_notification_topic_name() -> str:
    return os.environ["S3_NOTIFICATION_TOPIC_NAME"]


async def create_s3_bucket(s3_client: S3Client, sns_client: SNSClient) -> None:
    bucket_name = get_bucket_name()
    notification_queue_name = get_s3_notification_topic_name()
    log = logger.bind(bucket_name=bucket_name)

    try:
        await s3_client.create_bucket(Bucket=bucket_name)
        log.info("s3_bucket_created")
    except (s3_client.exceptions.BucketAlreadyExists, s3_client.exceptions.BucketAlreadyOwnedByYou):
        log.info("s3_bucket_already_exists")

    notification_topic = await sns_client.create_topic(Name=notification_queue_name)
    await s3_client.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration={
            "TopicConfigurations": [
                {
                    "TopicArn": notification_topic["TopicArn"],
                    "Events": ["s3:ObjectCreated:*"],
                }
            ],
        },
    )
    log.info("s3_bucket_notification_set", notification_topic_arn=notification_topic["TopicArn"])
