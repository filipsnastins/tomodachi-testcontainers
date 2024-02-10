"""WireMock testcontainer.

Adaptation of https://github.com/wiremock/python-wiremock
See WireMock usage examples in https://github.com/wiremock/python-wiremock/tree/master/examples
"""

import os
from pathlib import Path
from typing import Any, Optional

from testcontainers.core.waiting_utils import wait_for_logs

from ..utils import copy_files_to_container
from .common import WebContainer


class WireMockContainer(WebContainer):
    MAPPING_STUBS_DIR: Path = Path("/home/wiremock/mappings/")
    MAPPING_FILES_DIR: Path = Path("/home/wiremock/__files/")

    def __init__(
        self,
        image: str = "wiremock/wiremock:latest",
        internal_port: int = 8080,
        edge_port: Optional[int] = None,
        mapping_stubs: Optional[Path] = None,
        mapping_files: Optional[Path] = None,
        *,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image,
            internal_port=internal_port,
            edge_port=edge_port,
            **kwargs,
        )

        mapping_stubs_env = os.getenv("WIREMOCK_TESTCONTAINER_MAPPING_STUBS")
        mapping_files_env = os.getenv("WIREMOCK_TESTCONTAINER_MAPPING_FILES")

        self.mapping_stubs = mapping_stubs or (Path(mapping_stubs_env) if mapping_stubs_env else None)
        self.mapping_files = mapping_files or (Path(mapping_files_env) if mapping_files_env else None)

        if verbose or os.getenv("WIREMOCK_TESTCONTAINER_VERBOSE"):
            self.with_command("--verbose")

    def log_message_on_container_start(self) -> str:
        return f"Wiremock admin: http://localhost:{self.edge_port}/__admin"

    def start(self) -> "WireMockContainer":
        super().start()
        wait_for_logs(self, "port:", timeout=10.0)
        self.load_mappings_from_files()
        return self

    def load_mappings_from_files(self) -> None:
        self._copy_mapping_stubs_to_container()
        self._copy_mapping_files_to_container()
        self.reset_mappings()

    def delete_mappings(self) -> None:
        self.exec(["curl", "-X", "DELETE", f"http://localhost:{self.internal_port}/__admin/mappings"])

    def reset_mappings(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/__admin/mappings/reset"])

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
