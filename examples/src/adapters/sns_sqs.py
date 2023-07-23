import os

from aiobotocore.session import get_session
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient


def get_sns_client() -> SNSClient:
    session = get_session()
    return session.create_client(
        "sns",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.environ.get("AWS_SNS_ENDPOINT_URL"),
    )


def get_sqs_client() -> SQSClient:
    session = get_session()
    return session.create_client(
        "sqs",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.environ.get("AWS_SQS_ENDPOINT_URL"),
    )
