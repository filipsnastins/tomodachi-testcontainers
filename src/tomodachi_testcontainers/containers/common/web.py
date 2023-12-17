"""Abstract web container for services that expose HTTP port."""
import abc
import urllib.parse
from typing import Any, Optional

import requests
from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from .container import DockerContainer


class WebContainer(DockerContainer, abc.ABC):
    internal_port: int
    edge_port: int

    def __init__(
        self,
        image: str,
        internal_port: int,
        edge_port: int,
        http_healthcheck_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port
        self.http_healthcheck_path = http_healthcheck_path
        self.with_bind_ports(internal_port, edge_port)

    def get_internal_url(self) -> str:
        ip = self.get_container_internal_ip()
        return f"http://{ip}:{self.internal_port}"

    def get_external_url(self) -> str:
        host = self.get_container_host_ip()
        return f"http://{host}:{self.edge_port}"

    def start(self, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> "WebContainer":
        super().start()
        if self.http_healthcheck_path:
            url = urllib.parse.urljoin(self.get_external_url(), self.http_healthcheck_path)
            wait_for_http_healthcheck(url=url, timeout=timeout, interval=interval, status_code=status_code)
        return self


def wait_for_http_healthcheck(url: str, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> None:
    for attempt in Retrying(stop=stop_after_delay(timeout), wait=wait_fixed(interval), reraise=True):
        with attempt:
            response = requests.get(url, timeout=timeout)
            if response.status_code != status_code:
                raise RuntimeError(f"Healthcheck failed with HTTP status code: {response.status_code}")
