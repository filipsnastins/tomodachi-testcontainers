import abc
import contextlib
import logging
import os
from types import TracebackType
from typing import Any, Dict, Optional, Type, cast

import docker.errors
import shortuuid
import testcontainers.core.container
from docker.models.containers import Container
from testcontainers.core.utils import inside_container

from tomodachi_testcontainers.utils import setup_logger


class ContainerWithSameNameAlreadyExistsError(Exception):
    pass


class DockerContainer(testcontainers.core.container.DockerContainer, abc.ABC):
    _container: Optional[Container]
    _name: str
    _logger: logging.Logger

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.network = os.getenv("TESTCONTAINER_DOCKER_NETWORK") or "bridge"
        super().__init__(*args, **kwargs, network=self.network)

    def __enter__(self) -> "DockerContainer":
        try:
            return self.start()
        except ContainerWithSameNameAlreadyExistsError:
            raise
        except Exception:
            self._forward_container_logs_to_logger()
            self.stop()
            raise

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self._forward_container_logs_to_logger()
        self.stop()

    @abc.abstractmethod
    def log_message_on_container_start(self) -> str:
        """Returns a message that will be logged when the container starts."""

    def get_container_host_ip(self) -> str:
        host = self.get_docker_client().host()
        if not host:
            return "localhost"
        if inside_container() and not os.getenv("DOCKER_HOST"):
            gateway_ip = self.get_container_gateway_ip()
            if gateway_ip == host:
                return self.get_container_internal_ip()
            return gateway_ip
        return host

    def get_container_internal_ip(self) -> str:
        return self.docker_inspect()["NetworkSettings"]["Networks"][self.network]["IPAddress"]

    def get_container_gateway_ip(self) -> str:
        return self.docker_inspect()["NetworkSettings"]["Networks"][self.network]["Gateway"]

    def docker_inspect(self) -> Dict[str, Any]:
        return self.get_docker_client().get_container(self.get_wrapped_container().id)

    def start(self) -> "DockerContainer":
        self._set_container_name()
        self._setup_logger()
        self._start()
        self._log_message_on_container_start()
        return self

    def stop(self) -> None:
        with contextlib.suppress(docker.errors.NotFound):
            container = self._container or cast(Container, self.get_docker_client().client.containers.get(self._name))
            if os.getenv("TESTCONTAINER_GRACEFUL_STOP"):
                container.stop(timeout=int(os.getenv("TESTCONTAINER_GRACEFUL_STOP_TIMEOUT", 10)))
            container.remove(force=True, v=True)
        self._container = None

    def restart(self) -> None:
        self.get_wrapped_container().restart()

    def _set_container_name(self) -> None:
        self._name = self._name or f"testcontainer-{shortuuid.uuid()}"

    def _setup_logger(self) -> None:
        self._logger = setup_logger(f"{self.__class__.__name__} ({self._name})")

    def _start(self) -> None:
        self._logger.info(f"Pulling image: {self.image}")
        try:
            self._container = self.get_docker_client().run(
                image=self.image,
                command=self._command or "",
                detach=True,
                environment=self.env,
                ports=self.ports,
                name=self._name,
                volumes=self.volumes,
                **self._kwargs,
            )
        except Exception as exc:
            self._logger.exception("Failed to start the container")
            if isinstance(exc, docker.errors.APIError) and exc.status_code == 409:  # pylint: disable=no-member
                raise ContainerWithSameNameAlreadyExistsError(self._name) from exc
            raise
        else:
            self._logger.info(f"Container started: {self._name}")

    def _log_message_on_container_start(self) -> None:
        if message := self.log_message_on_container_start():
            self._logger.info(message)

    def _forward_container_logs_to_logger(self) -> None:
        if container := self.get_wrapped_container():
            logs = bytes(container.logs(timestamps=True)).decode().split("\n")
            for log in logs:
                self._logger.info(log)
