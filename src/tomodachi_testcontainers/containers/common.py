import io
import logging
import os
import subprocess  # nosec: B404
import tarfile
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple, cast

import requests
import testcontainers.core.container
from docker.errors import ImageNotFound
from docker.models.containers import Container
from docker.models.images import Image as DockerImage
from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import inside_container


class DockerContainer(testcontainers.core.container.DockerContainer):
    def __init__(self, *args: Any, network: Optional[str] = None, **kwargs: Any) -> None:
        self.network = network or os.getenv("TESTCONTAINER_DOCKER_NETWORK") or "bridge"
        super().__init__(*args, **kwargs, network=self.network)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        logger = logging.getLogger(self.__class__.__name__)
        logs = self.get_wrapped_container().logs(timestamps=True).decode().split("\n")
        for log in logs:
            logger.info(log)
        self.stop()

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
        container = self.get_docker_client().get_container(self.get_wrapped_container().id)
        return container["NetworkSettings"]["Networks"][self.network]["IPAddress"]

    def get_container_gateway_ip(self) -> str:
        container = self.get_docker_client().get_container(self.get_wrapped_container().id)
        return container["NetworkSettings"]["Networks"][self.network]["Gateway"]

    def restart_container(self) -> None:
        self.get_wrapped_container().restart()


class EphemeralDockerImage:
    """Builds a Docker image from a given Dockerfile and removes it when the context manager exits."""

    image: DockerImage

    def __init__(
        self,
        dockerfile: Optional[Path] = None,
        context: Optional[Path] = None,
        target: Optional[str] = None,
        docker_client_kw: Optional[Dict] = None,
    ) -> None:
        self.dockerfile = str(dockerfile) if dockerfile else None
        self.context = str(context) if context else "."
        self.target = target
        self.client = DockerClient(**(docker_client_kw or {}))

    def __enter__(self) -> DockerImage:
        self.image = self.build_image()
        return self.image

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_image()

    def build_image(self) -> DockerImage:
        if os.getenv("DOCKER_BUILDKIT"):
            return self._build_with_docker_buildkit()
        return self._build_with_docker_client()

    def remove_image(self) -> None:
        self.client.client.images.remove(image=str(self.image.id))

    def _build_with_docker_buildkit(self) -> DockerImage:
        cmd = ["docker", "build", "-q", "--rm=true"]
        if self.dockerfile:
            cmd.extend(["-f", self.dockerfile])
        if self.target:
            cmd.extend(["--target", self.target])
        cmd.append(self.context)

        result = subprocess.run(
            cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )  # nosec: B603
        image_id = result.stdout.decode("utf-8").strip()
        return cast(DockerImage, self.client.client.images.get(image_id))

    def _build_with_docker_client(self) -> DockerImage:
        image, _ = cast(
            Tuple[DockerImage, Iterator],
            self.client.client.images.build(
                dockerfile=self.dockerfile,
                path=self.context,
                target=self.target,
                forcerm=True,
            ),
        )
        return image


def get_docker_image(image_id: str, docker_client_kw: Optional[Dict] = None) -> DockerImage:
    client = DockerClient(**(docker_client_kw or {}))
    try:
        return cast(DockerImage, client.client.images.get(image_id))
    except ImageNotFound:
        return cast(DockerImage, client.client.images.pull(image_id))


def copy_folder_to_container(host_path: Path, container_path: Path, container: Container) -> None:
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        for root, _, files in os.walk(host_path):
            for file in files:
                file_path = Path(root) / file
                arcname = os.path.relpath(file_path, host_path)
                tar.add(file_path, arcname=arcname)
    tar_stream.seek(0)
    container.put_archive(path=container_path, data=tar_stream)


def wait_for_http_healthcheck(url: str, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> None:
    for attempt in Retrying(stop=stop_after_delay(timeout), wait=wait_fixed(interval), reraise=True):
        with attempt:
            response = requests.get(url, timeout=timeout)
            if response.status_code != status_code:
                raise RuntimeError(f"Healthcheck failed with HTTP status code: {response.status_code}")
