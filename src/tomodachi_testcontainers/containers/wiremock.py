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
    MAPPING_STUBS_DIR: Path = Path("/home/wiremock/mappings/")
    MAPPING_FILES_DIR: Path = Path("/home/wiremock/__files/")

    def __init__(
        self,
        image: str = "wiremock/wiremock:latest",
        internal_port: int = 8080,
        edge_port: int = 8080,
        mapping_stubs: Optional[Path] = None,
        mapping_files: Optional[Path] = None,
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

    def start(self) -> "WireMockContainer":
        super().start()
        wait_for_logs(self, "port:", timeout=10.0)
        self.load_mappings()
        return self

    def load_mappings(self) -> None:
        self._copy_mapping_stubs_to_container()
        self._copy_mapping_files_to_container()
        self._reload_mappings()

    def _copy_mapping_stubs_to_container(self) -> None:
        if self.mapping_stubs is not None:
            copy_files_to_container(
                self.get_wrapped_container(), host_path=self.mapping_stubs, container_path=self.MAPPING_STUBS_DIR
            )

    def _copy_mapping_files_to_container(self) -> None:
        if self.mapping_files is not None:
            copy_files_to_container(
                self.get_wrapped_container(), host_path=self.mapping_files, container_path=self.MAPPING_FILES_DIR
            )

    def _reload_mappings(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/__admin/mappings/reset"])
