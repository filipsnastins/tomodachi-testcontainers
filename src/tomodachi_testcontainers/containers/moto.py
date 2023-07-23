import os
from typing import Any, Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

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

        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-1"
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID") or "testing"  # nosec: B105
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY") or "testing"  # nosec: B105

        self.with_bind_ports(self.internal_port, self.edge_port)
        self.with_env("AWS_DEFAULT_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", self.aws_access_key_id)
        self.with_env("AWS_SECRET_ACCESS_KEY", self.aws_secret_access_key)

    def get_internal_url(self) -> str:
        bridge_ip = self.get_docker_client().bridge_ip(self.get_wrapped_container().id)
        return f"http://{bridge_ip}:{self.internal_port}"

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

    def start(self, timeout: float = 10) -> "MotoContainer":
        super().start()
        wait_for_logs(self, "Running on all addresses", timeout=timeout)
        return self

    def reset(self) -> None:
        self.exec(["sh", "-c", "curl", "-X", "POST", f"http://localhost:{self.internal_port}/moto-api/reset"])
