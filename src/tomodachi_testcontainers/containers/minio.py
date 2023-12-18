import os
from typing import Any, Optional

from tomodachi_testcontainers.utils import AWSClientConfig

from .common import WebContainer


class MinioContainer(WebContainer):
    def __init__(
        self,
        image: str = "minio/minio:latest",
        s3_api_internal_port: int = 9000,
        s3_api_edge_port: int = 9000,
        console_internal_port: int = 9001,
        console_edge_port: int = 9001,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image,
            internal_port=s3_api_internal_port,
            edge_port=s3_api_edge_port,
            http_healthcheck_path="/minio/health/live",
            **kwargs,
        )
        self.s3_api_internal_port = s3_api_internal_port
        self.s3_api_edge_port = s3_api_edge_port
        self.console_internal_port = console_internal_port
        self.console_edge_port = console_edge_port

        self.with_bind_ports(console_internal_port, console_edge_port)

        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        self.minio_root_user = os.getenv("MINIO_ROOT_USER") or "minioadmin"  # nosec: B105
        self.minio_root_password = os.getenv("MINIO_ROOT_PASSWORD") or "minioadmin"  # nosec: B105

        self.with_env("MINIO_ROOT_USER", self.minio_root_user)
        self.with_env("MINIO_ROOT_PASSWORD", self.minio_root_password)

        self.with_command(
            f'server /data --address ":{self.s3_api_internal_port}" --console-address ":{self.console_internal_port}"'
        )

    def log_message_on_container_start(self) -> str:
        return (
            "Minio started: "
            f"S3-API: http://localhost:{self.s3_api_edge_port}/; "  # noqa: E702
            f"console: http://localhost:{self.console_edge_port}/"
        )

    def get_aws_client_config(self) -> AWSClientConfig:
        return AWSClientConfig(
            region_name=self.region_name,
            aws_access_key_id=self.minio_root_user,
            aws_secret_access_key=self.minio_root_password,
            endpoint_url=self.get_external_url(),
        )

    def reset_minio(self) -> None:
        self.exec(["mc", "rm", "--recursive", "--dangerous", "--force", "data/"])
