import os
from contextlib import suppress
from pathlib import Path
from typing import Any, Optional

import shortuuid
from testcontainers.core.waiting_utils import wait_for_logs

from ..utils import copy_files_from_container
from .common import WebContainer


class TomodachiContainer(WebContainer):
    """Tomodachi container.

    Configuration environment variables (set on host machine):

    - `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE` - defaults to `False`
    """

    def __init__(
        self,
        image: str,
        internal_port: int = 9700,
        edge_port: Optional[int] = None,
        http_healthcheck_path: Optional[str] = None,
        *,
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
        self._export_coverage = export_coverage or bool(os.getenv("TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE"))
        if self._export_coverage:
            self._configure_coverage_export()

    def log_message_on_container_start(self) -> str:
        return f"Tomodachi service: http://localhost:{self.edge_port}"

    def start(self) -> "TomodachiContainer":
        super().start()
        # Apart from HTTP healthcheck, we need to wait for "started service" log
        # to make sure messaging transport like AWS SNS SQS is also up and running.
        # It's started independently from HTTP transport.

        # Different service start messages depending on tomodachi version
        # tomodachi < 0.26.0 - "Started service"
        # tomodachi >= 0.26.0 - "started service successfully"
        # using (?i) to ignore case to support both versions
        wait_for_logs(self, "(?i)started service", timeout=10.0)
        return self

    def stop(self) -> None:
        if self._export_coverage:
            with suppress(Exception):
                self._stop_container_and_copy_coverage_report()
        super().stop()

    def _configure_coverage_export(self) -> None:
        self._coverage_file_path = f"/tmp/.coverage.testcontainer.{shortuuid.uuid()}"  # nosec: B108
        self.with_env("COVERAGE_FILE", self._coverage_file_path)

    def _stop_container_and_copy_coverage_report(self) -> None:
        container = self.get_wrapped_container()
        container.stop()
        copy_files_from_container(container, container_path=Path(self._coverage_file_path), host_path=Path(os.getcwd()))
