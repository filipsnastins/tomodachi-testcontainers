import contextlib

import pytest

from tomodachi_testcontainers.pytest.localstack_fixtures import (
    _restart_localstack_container,
    localstack_container,
    localstack_dynamodb_client,
    localstack_s3_client,
    localstack_sns_client,
    localstack_sqs_client,
    localstack_ssm_client,
)
from tomodachi_testcontainers.pytest.moto_fixtures import (
    _reset_moto_container,
    moto_container,
    moto_dynamodb_client,
    moto_s3_client,
    moto_sns_client,
    moto_sqs_client,
    moto_ssm_client,
)
from tomodachi_testcontainers.pytest.tomodachi_fixtures import tomodachi_image

with contextlib.suppress(ModuleNotFoundError):
    from tomodachi_testcontainers.pytest.sftp_fixtures import sftp_container, userpass_sftp_client, userssh_sftp_client


pytest.register_assert_rewrite("tomodachi_testcontainers.pytest.assertions")


__all__ = [
    "_reset_moto_container",
    "_restart_localstack_container",
    "localstack_container",
    "localstack_dynamodb_client",
    "localstack_s3_client",
    "localstack_sns_client",
    "localstack_sqs_client",
    "localstack_ssm_client",
    "moto_container",
    "moto_dynamodb_client",
    "moto_s3_client",
    "moto_sns_client",
    "moto_sqs_client",
    "moto_ssm_client",
    "sftp_container",
    "tomodachi_image",
    "userpass_sftp_client",
    "userssh_sftp_client",
]
