"""pytest fixtures."""

from contextlib import suppress

from .containers import testcontainer_image
from .localstack import (
    localstack_container,
    localstack_dynamodb_client,
    localstack_iam_client,
    localstack_lambda_client,
    localstack_s3_client,
    localstack_sns_client,
    localstack_snssqs_tc,
    localstack_sqs_client,
    localstack_ssm_client,
    restart_localstack_container_on_teardown,
)
from .minio import minio_container, minio_s3_client
from .moto import (
    moto_container,
    moto_dynamodb_client,
    moto_iam_client,
    moto_lambda_client,
    moto_s3_client,
    moto_sns_client,
    moto_snssqs_tc,
    moto_sqs_client,
    moto_ssm_client,
    reset_moto_container_on_teardown,
)
from .wiremock import reset_wiremock_container_on_teardown, wiremock_container

with suppress(ImportError):  # 'mysql' extra dependency
    from .mysql import mysql_container

with suppress(ImportError):  # 'postgres' extra dependency
    from .postgres import postgres_container

with suppress(ImportError):  # 'sftp' extra dependency
    from .sftp import sftp_container, userpass_sftp_client, userssh_sftp_client


__all__ = [
    "reset_moto_container_on_teardown",
    "reset_wiremock_container_on_teardown",
    "restart_localstack_container_on_teardown",
    "localstack_container",
    "localstack_dynamodb_client",
    "localstack_iam_client",
    "localstack_lambda_client",
    "localstack_s3_client",
    "localstack_sns_client",
    "localstack_snssqs_tc",
    "localstack_sqs_client",
    "localstack_ssm_client",
    "minio_container",
    "minio_s3_client",
    "moto_container",
    "moto_dynamodb_client",
    "moto_iam_client",
    "moto_lambda_client",
    "moto_s3_client",
    "moto_sns_client",
    "moto_snssqs_tc",
    "moto_sqs_client",
    "moto_ssm_client",
    "mysql_container",
    "postgres_container",
    "sftp_container",
    "testcontainer_image",
    "userpass_sftp_client",
    "userssh_sftp_client",
    "wiremock_container",
]
