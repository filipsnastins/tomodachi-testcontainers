import contextlib

from .containers.common import DockerContainer, EphemeralDockerImage, WebContainer
from .containers.dynamodb_admin import DynamoDBAdminContainer
from .containers.localstack import LocalStackContainer
from .containers.minio import MinioContainer
from .containers.moto import MotoContainer
from .containers.tomodachi import TomodachiContainer
from .containers.wiremock import WireMockContainer

with contextlib.suppress(ImportError):  # 'db' extra dependency
    from .containers.common import DatabaseContainer

with contextlib.suppress(ImportError):  # 'mysql' extra dependency
    from .containers.mysql import MySQLContainer

with contextlib.suppress(ImportError):  # 'postgres' extra dependency
    from .containers.postgres import PostgreSQLContainer

with contextlib.suppress(ImportError):  # 'sftp' extra dependency
    from .containers.sftp import SFTPContainer

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
