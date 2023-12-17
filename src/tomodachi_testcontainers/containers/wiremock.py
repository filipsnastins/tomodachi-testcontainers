"""WireMock testcontainer.

Adaptation of https://github.com/wiremock/python-wiremock
See WireMock usage examples in https://github.com/wiremock/python-wiremock/tree/master/examples
"""
from pathlib import Path
from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.utils import copy_files_to_container

from .common import WebContainer


class WireMockContainer(WebContainer):
    MAPPINGS_DIR: Path = Path("/home/wiremock/mappings/")
    FILES_DIR: Path = Path("/home/wiremock/__files/")

    def __init__(
        self,
        mapping_stubs: Optional[Path] = None,
        mapping_files: Optional[Path] = None,
        image: str = "wiremock/wiremock:latest",
        internal_port: int = 8080,
        edge_port: int = 8080,
        *,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, internal_port=internal_port, edge_port=edge_port, **kwargs)

        self.mapping_stubs = mapping_stubs
        self.mapping_files = mapping_files

        if verbose:
            self.with_command("--verbose")

    def log_message_on_container_start(self) -> str:
        return f"Wiremock admin: http://localhost:{self.edge_port}/__admin"

    def start(self, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> "WireMockContainer":
        super().start(timeout=timeout, interval=interval, status_code=status_code)
        wait_for_logs(self, "port:", timeout=timeout)
        self.copy_mappings_to_container()
        self.copy_mapping_files_to_container()
        self.reload_mappings()
        return self

    def copy_mappings_to_container(self) -> None:
        if self.mapping_stubs is not None:
            copy_files_to_container(
                self.get_wrapped_container(), host_path=self.mapping_stubs, container_path=self.MAPPINGS_DIR
            )

    def copy_mapping_files_to_container(self) -> None:
        if self.mapping_files is not None:
            copy_files_to_container(
                self.get_wrapped_container(), host_path=self.mapping_files, container_path=self.FILES_DIR
            )

    def reload_mappings(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/__admin/mappings/reset"])
