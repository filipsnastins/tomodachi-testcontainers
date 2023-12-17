import contextlib

from .common import DockerContainer, EphemeralDockerImage, WebContainer
from .dynamodb_admin import DynamoDBAdminContainer
from .localstack import LocalStackContainer
from .minio import MinioContainer
from .moto import MotoContainer
from .tomodachi import TomodachiContainer
from .wiremock import WireMockContainer

with contextlib.suppress(ImportError):  # 'db' extra dependency
    from .common import DatabaseContainer

with contextlib.suppress(ImportError):  # 'mysql' extra dependency
    from .mysql import MySQLContainer

with contextlib.suppress(ImportError):  # 'postgres' extra dependency
    from .postgres import PostgreSQLContainer

with contextlib.suppress(ImportError):  # 'sftp' extra dependency
    from .sftp import SFTPContainer

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
