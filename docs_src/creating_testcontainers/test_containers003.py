from typing import Generator, cast

import pytest
import requests

from tomodachi_testcontainers import WebContainer


class HTTPBinContainer(WebContainer):
    def __init__(self, internal_port: int = 80, edge_port: int | None = None) -> None:
        super().__init__(
            image="kennethreitz/httpbin",
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path="/status/200",
        )

    def log_message_on_container_start(self) -> str:
        return f"HTTPBin container: {self.get_external_url()}"


@pytest.fixture(scope="session")
def httpbin_container() -> Generator[HTTPBinContainer, None, None]:
    with HTTPBinContainer() as container:
        yield cast(HTTPBinContainer, container)


def test_httpbin_container_started(httpbin_container: HTTPBinContainer) -> None:
    base_url = httpbin_container.get_external_url()

    response = requests.get(f"{base_url}/status/200", timeout=10)

    assert response.status_code == 200
