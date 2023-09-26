from __future__ import annotations

import urllib.parse
from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import DockerContainer, wait_for_http_healthcheck


class TomodachiContainer(DockerContainer):
    def __init__(
        self,
        image: str,
        internal_port: int = 9700,
        edge_port: int = 9700,
        http_healthcheck_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port
        self.http_healthcheck_path = http_healthcheck_path
        self.with_bind_ports(internal_port, edge_port)

    def __enter__(self) -> TomodachiContainer:
        self.logger.info(f"Tomodachi service: http://localhost:{self.edge_port}")
        return self.start()

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def start(self, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> "TomodachiContainer":
        super().start()
        if self.http_healthcheck_path:
            url = urllib.parse.urljoin(self.get_external_url(), self.http_healthcheck_path)
            wait_for_http_healthcheck(url=url, timeout=timeout, interval=interval, status_code=status_code)

        # Apart from HTTP healthcheck, we need to wait for "started service" log
        # to make sure messaging transport like AWS SNS SQS is also up and running.
        # It's started independently from HTTP transport.

        # Different service start messages depending on tomodachi version
        # tomodachi < 0.26.0 - "Started service"
        # tomodachi >= 0.26.0 - "started service successfully"
        # using (?i) to ignore case to support both versions
        wait_for_logs(self, "(?i)started service", timeout=timeout)
        return self
