from typing import Generator, cast

import pytest
from requests.exceptions import ConnectionError

from tomodachi_testcontainers.containers import DockerContainer, wait_for_http_healthcheck
from tomodachi_testcontainers.utils import get_available_port


class HTTPBinContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="kennethreitz/httpbin")
        self.edge_port = get_available_port()
        self.with_bind_ports(80, self.edge_port)

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"


@pytest.fixture()
def httpbin_container() -> Generator[HTTPBinContainer, None, None]:
    with HTTPBinContainer() as container:
        yield cast(HTTPBinContainer, container)


def test_no_connection_to_host() -> None:
    with pytest.raises(ConnectionError):
        wait_for_http_healthcheck(f"http://localhost:{get_available_port()}/foo", timeout=1.0)


def test_healthcheck_returns_http_500(httpbin_container: HTTPBinContainer) -> None:
    with pytest.raises(RuntimeError, match="Healthcheck failed with HTTP status code: 500"):
        wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/500", timeout=1.0)


def test_healthcheck_returns_http_200(httpbin_container: HTTPBinContainer) -> None:
    wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/200")
