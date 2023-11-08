from typing import Generator, cast

import pytest
from requests.exceptions import ConnectionError

from tomodachi_testcontainers import WebContainer
from tomodachi_testcontainers.containers.common.web import wait_for_http_healthcheck
from tomodachi_testcontainers.utils import get_available_port


class HTTPBinContainer(WebContainer):
    def __init__(self) -> None:
        super().__init__(image="kennethreitz/httpbin", internal_port=80, edge_port=get_available_port())

    def log_message_on_container_start(self) -> str:
        return "HTTPBin container started"


@pytest.fixture(scope="module")
def httpbin_container() -> Generator[HTTPBinContainer, None, None]:
    with HTTPBinContainer() as container:
        yield cast(HTTPBinContainer, container)


def test_no_connection_to_host() -> None:
    with pytest.raises(ConnectionError):
        wait_for_http_healthcheck(f"http://localhost:{get_available_port()}/foo", timeout=2.0)


def test_healthcheck_returns_http_500(httpbin_container: HTTPBinContainer) -> None:
    with pytest.raises(RuntimeError, match="Healthcheck failed with HTTP status code: 500"):
        wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/500", timeout=2.0)


def test_healthcheck_returns_http_200(httpbin_container: HTTPBinContainer) -> None:
    wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/200")
