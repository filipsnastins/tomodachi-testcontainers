import os
from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.utils import AWSClientConfig

from .common import WebContainer


class MotoContainer(WebContainer):
    def __init__(
        self,
        image: str = "motoserver/moto:latest",
        internal_port: int = 5000,
        edge_port: int = 5000,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image,
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path="/moto-api/data.json",
            **kwargs,
        )

        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID") or "testing"  # nosec: B105
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") or "testing"  # nosec: B105

        self.with_env("AWS_DEFAULT_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", self.aws_access_key_id)
        self.with_env("AWS_SECRET_ACCESS_KEY", self.aws_secret_access_key)

        self.with_env("MOTO_PORT", str(self.internal_port))

        # Docker is needed for running AWS Lambda container
        self.with_env("MOTO_DOCKER_NETWORK_NAME", self.network)
        self.with_volume_mapping("/var/run/docker.sock", "/var/run/docker.sock")

    def log_message_on_container_start(self) -> str:
        return f"Moto dashboard: http://localhost:{self.edge_port}/moto-api"

    def get_aws_client_config(self) -> AWSClientConfig:
        return AWSClientConfig(
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.get_external_url(),
        )

    def start(self, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> "MotoContainer":
        super().start(timeout=timeout, interval=interval, status_code=status_code)
        wait_for_logs(self, "Running on all addresses", timeout=timeout)
        return self

    def reset_moto(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/moto-api/reset"])
