import contextlib
import os
from pathlib import Path
from typing import Any, Optional

import shortuuid
from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import WebContainer
from tomodachi_testcontainers.utils import copy_from_container


class TomodachiContainer(WebContainer):
    def __init__(
        self,
        image: str,
        internal_port: int = 9700,
        edge_port: int = 9700,
        http_healthcheck_path: Optional[str] = None,
        export_coverage: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image=image,
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path=http_healthcheck_path,
            **kwargs,
        )
        self._export_coverage = export_coverage
        if self._export_coverage:
            self._configure_coverage_export()

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

    def stop(self) -> None:
        if self._export_coverage:
            self._copy_coverage()
        super().stop()

    def _configure_coverage_export(self) -> None:
        self._coverage_file_path = f"/tmp/.coverage.testcontainer.{shortuuid.uuid()}"
        self.with_env("COVERAGE_FILE", self._coverage_file_path)

    def _copy_coverage(self) -> None:
        with contextlib.suppress(Exception):
            container = self.get_wrapped_container()
            container.stop()
            copy_from_container(container, container_path=Path(self._coverage_file_path), host_path=Path(os.getcwd()))
