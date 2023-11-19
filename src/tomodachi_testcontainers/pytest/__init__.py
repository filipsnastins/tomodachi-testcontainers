import contextlib

import pytest

from tomodachi_testcontainers.pytest.fixtures.containers import testcontainers_docker_image
from tomodachi_testcontainers.pytest.fixtures.localstack import (
    _restart_localstack_container_on_teardown,
    localstack_container,
    localstack_dynamodb_client,
    localstack_iam_client,
    localstack_lambda_client,
    localstack_s3_client,
    localstack_sns_client,
    localstack_snssqs_tc,
    localstack_sqs_client,
    localstack_ssm_client,
)
from tomodachi_testcontainers.pytest.fixtures.minio import minio_container, minio_s3_client
from tomodachi_testcontainers.pytest.fixtures.moto import (
    _reset_moto_container_on_teardown,
    moto_container,
    moto_dynamodb_client,
    moto_iam_client,
    moto_lambda_client,
    moto_s3_client,
    moto_sns_client,
    moto_snssqs_tc,
    moto_sqs_client,
    moto_ssm_client,
)

with contextlib.suppress(ImportError):  # 'mysql' extra dependency
    from tomodachi_testcontainers.pytest.fixtures.mysql import mysql_container

with contextlib.suppress(ImportError):  # 'postgres' extra dependency
    from tomodachi_testcontainers.pytest.fixtures.postgres import postgres_container

with contextlib.suppress(ImportError):  # 'sftp' extra dependency
    from tomodachi_testcontainers.pytest.fixtures.sftp import sftp_container, userpass_sftp_client, userssh_sftp_client


pytest.register_assert_rewrite("tomodachi_testcontainers.pytest.assertions")


__all__ = [
    "_reset_moto_container_on_teardown",
    "_restart_localstack_container_on_teardown",
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
    "testcontainers_docker_image",
    "userpass_sftp_client",
    "userssh_sftp_client",
]
