from typing import Generator

import pytest
import requests
from testcontainers.core.waiting_utils import wait_for_logs

from tomodachi_testcontainers import DockerContainer
from tomodachi_testcontainers.utils import get_available_port


class HTTPBinContainer(DockerContainer):
    def __init__(self, internal_port: int = 80, edge_port: int | None = None) -> None:
        super().__init__(image="kennethreitz/httpbin")
        self.with_bind_ports(internal_port, edge_port or get_available_port())

    def log_message_on_container_start(self) -> str:
        return f"HTTPBin container: http://localhost:{self.get_exposed_port(80)}"

    def start(self, timeout: int = 60) -> "HTTPBinContainer":
        super().start()
        wait_for_logs(self, r"Listening at", timeout=timeout)
        return self


@pytest.fixture(scope="session")
def httpbin_container() -> Generator[DockerContainer, None, None]:
    with HTTPBinContainer() as container:
        yield container


def test_httpbin_container_started(httpbin_container: HTTPBinContainer) -> None:
    base_url = f"http://localhost:{httpbin_container.get_exposed_port(80)}"

    response = requests.get(f"{base_url}/status/200", timeout=10)

    assert response.status_code == 200
