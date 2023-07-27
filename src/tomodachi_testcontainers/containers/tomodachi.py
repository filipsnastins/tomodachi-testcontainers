from typing import Any

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import DockerContainer


class TomodachiContainer(DockerContainer):
    def __init__(self, image: str, internal_port: int = 9700, edge_port: int = 9700, **kwargs: Any) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port
        self.with_bind_ports(internal_port, edge_port)

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def start(self, timeout: float = 10) -> "TomodachiContainer":
        super().start()
        wait_for_logs(self, "Started service", timeout=timeout)
        return self
