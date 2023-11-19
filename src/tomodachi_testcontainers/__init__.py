import contextlib

from tomodachi_testcontainers.containers.common import DockerContainer, EphemeralDockerImage, WebContainer
from tomodachi_testcontainers.containers.dynamodb_admin import DynamoDBAdminContainer
from tomodachi_testcontainers.containers.localstack import LocalStackContainer
from tomodachi_testcontainers.containers.minio import MinioContainer
from tomodachi_testcontainers.containers.moto import MotoContainer
from tomodachi_testcontainers.containers.tomodachi import TomodachiContainer
from tomodachi_testcontainers.containers.wiremock import WireMockContainer

with contextlib.suppress(ImportError):  # 'db' extra dependency
    from tomodachi_testcontainers.containers.common import DatabaseContainer

with contextlib.suppress(ImportError):  # 'mysql' extra dependency
    from tomodachi_testcontainers.containers.mysql import MySQLContainer

with contextlib.suppress(ImportError):  # 'postgres' extra dependency
    from tomodachi_testcontainers.containers.postgres import PostgreSQLContainer

with contextlib.suppress(ImportError):  # 'sftp' extra dependency
    from tomodachi_testcontainers.containers.sftp import SFTPContainer

__all__ = [
    "DatabaseContainer",
    "DockerContainer",
    "DynamoDBAdminContainer",
    "EphemeralDockerImage",
    "LocalStackContainer",
    "MinioContainer",
    "MotoContainer",
    "MySQLContainer",
    "PostgreSQLContainer",
    "SFTPContainer",
    "TomodachiContainer",
    "WebContainer",
    "WireMockContainer",
]
