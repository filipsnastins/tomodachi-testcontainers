import pytest
from requests.exceptions import ConnectionError

from tests.conftest import HTTPBinContainer
from tomodachi_testcontainers.containers.common.web import wait_for_http_healthcheck
from tomodachi_testcontainers.utils import get_available_port


def test_no_connection_to_host() -> None:
    with pytest.raises(ConnectionError):
        wait_for_http_healthcheck(f"http://localhost:{get_available_port()}/foo", timeout=1.0)


def test_healthcheck_returns_http_500(httpbin_container: HTTPBinContainer) -> None:
    with pytest.raises(RuntimeError, match="Healthcheck failed with HTTP status code: 500"):
        wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/500", timeout=1.0)


def test_healthcheck_returns_http_200(httpbin_container: HTTPBinContainer) -> None:
    wait_for_http_healthcheck(f"{httpbin_container.get_external_url()}/status/200")
