from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import WebContainer


class TomodachiContainer(WebContainer):
    def __init__(
        self,
        image: str,
        internal_port: int = 9700,
        edge_port: int = 9700,
        http_healthcheck_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image=image,
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path=http_healthcheck_path,
            **kwargs,
        )

    def log_message_on_container_start(self) -> str:
        return f"Tomodachi service: http://localhost:{self.edge_port}"

    def start(self, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> "TomodachiContainer":
        super().start(timeout=timeout, interval=interval, status_code=status_code)
        # Apart from HTTP healthcheck, we need to wait for "started service" log
        # to make sure messaging transport like AWS SNS SQS is also up and running.
        # It's started independently from HTTP transport.

        # Different service start messages depending on tomodachi version
        # tomodachi < 0.26.0 - "Started service"
        # tomodachi >= 0.26.0 - "started service successfully"
        # using (?i) to ignore case to support both versions
        wait_for_logs(self, "(?i)started service", timeout=timeout)
        return self
