"""WireMock testcontainer.

Adaptation of https://github.com/wiremock/python-wiremock
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers.containers.common import DockerContainer, copy_folder_to_container


class WireMockContainer(DockerContainer):
    MAPPINGS_DIR: Path = Path("/home/wiremock/mappings/")
    FILES_DIR: Path = Path("/home/wiremock/__files/")

    def __init__(
        self,
        mapping_stubs: Path,
        mapping_files: Path,
        image: str = "wiremock/wiremock:latest",
        internal_port: int = 8080,
        edge_port: int = 8080,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.mapping_stubs = mapping_stubs
        self.mapping_files = mapping_files

        self.internal_port = internal_port
        self.edge_port = edge_port
        self.with_bind_ports(self.internal_port, self.edge_port)

        if verbose:
            self.with_command("--verbose")

    def __enter__(self) -> WireMockContainer:
        self.logger.info(f"Wiremock admin: http://localhost:{self.edge_port}/__admin")
        return self.start()

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def start(self, timeout: float = 10.0) -> "WireMockContainer":
        super().start()
        wait_for_logs(self, "port:", timeout=timeout)
        self.copy_mappings_to_container()
        self.copy_mapping_files_to_container()
        self.reload_mappings()
        return self

    def copy_mappings_to_container(self) -> None:
        copy_folder_to_container(
            host_path=self.mapping_stubs, container_path=self.MAPPINGS_DIR, container=self.get_wrapped_container()
        )

    def copy_mapping_files_to_container(self) -> None:
        copy_folder_to_container(
            host_path=self.mapping_files, container_path=self.FILES_DIR, container=self.get_wrapped_container()
        )

    def reload_mappings(self) -> None:
        self.exec(["curl", "-X", "POST", f"http://localhost:{self.internal_port}/__admin/mappings/reset"])
