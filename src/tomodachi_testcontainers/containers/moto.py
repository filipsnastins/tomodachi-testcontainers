from __future__ import annotations

import os
from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import DockerContainer
from tomodachi_testcontainers.utils import AWSClientConfig


class MotoContainer(DockerContainer):
    def __init__(
        self,
        image: str = "motoserver/moto:latest",
        internal_port: int = 5000,
        edge_port: int = 5000,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port

        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID") or "testing"  # nosec: B105
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") or "testing"  # nosec: B105

        self.with_bind_ports(self.internal_port, self.edge_port)
        self.with_env("AWS_DEFAULT_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", self.aws_access_key_id)
        self.with_env("AWS_SECRET_ACCESS_KEY", self.aws_secret_access_key)

        self.with_env("MOTO_PORT", str(self.internal_port))

        # Docker is needed for running AWS Lambda container
        self.with_env("MOTO_DOCKER_NETWORK_NAME", self.network)
        self.with_volume_mapping("/var/run/docker.sock", "/var/run/docker.sock")

    def __enter__(self) -> MotoContainer:
        self.logger.info(f"Moto dashboard: http://localhost:{self.edge_port}/moto-api")
        return self.start()

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def get_aws_client_config(self) -> AWSClientConfig:
        return AWSClientConfig(
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.get_external_url(),
        )

    def start(self, timeout: float = 10.0) -> "MotoContainer":
        super().start()
        wait_for_logs(self, "Running on all addresses", timeout=timeout)
        return self

    def reset_moto(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/moto-api/reset"])
