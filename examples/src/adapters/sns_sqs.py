import os

from types_aiobotocore_sns import SNSClient

from .aws import session


def get_sns_client() -> SNSClient:
    return session.create_client(
        "sns",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_SNS_ENDPOINT_URL"),
    )
