import os

from aiobotocore.session import get_session
from types_aiobotocore_s3 import S3Client

session = get_session()


def get_bucket_name() -> str:
    return os.environ["AWS_S3_BUCKET_NAME"]


def get_s3_client() -> S3Client:
    return session.create_client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
    )
