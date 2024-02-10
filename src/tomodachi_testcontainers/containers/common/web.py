"""Abstract web container for services that expose HTTP port."""

import abc
import urllib.parse
from typing import Any, Optional

import requests
from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from ...utils import get_available_port
from .container import DockerContainer


class WebContainer(DockerContainer, abc.ABC):
    """Abstract class for web application containers."""

    internal_port: int
    edge_port: int

    def __init__(
        self,
        image: str,
        internal_port: int,
        edge_port: Optional[int] = None,
        http_healthcheck_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port or get_available_port()
        self.http_healthcheck_path = http_healthcheck_path
        self.with_bind_ports(internal_port, self.edge_port)

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def start(self) -> "WebContainer":
        super().start()
        if self.http_healthcheck_path:
            url = urllib.parse.urljoin(self.get_external_url(), self.http_healthcheck_path)
            wait_for_http_healthcheck(url=url)
        return self


def wait_for_http_healthcheck(
    url: str,
    interval: float = 1.0,
    timeout: float = 3.0,
    start_period: float = 10.0,
    retries: int = 3,
    status_code: int = 200,
) -> None:
    for attempt in Retrying(
        stop=stop_after_delay(start_period + (timeout * retries)),
        wait=wait_fixed(interval),
        reraise=True,
    ):
        with attempt:
            response = requests.get(url, timeout=timeout)
            if response.status_code != status_code:
                raise RuntimeError(f"Healthcheck failed with HTTP status code: {response.status_code}")
