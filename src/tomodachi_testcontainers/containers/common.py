import os
import pathlib
from typing import Any, Dict, Iterator, Optional, Tuple, cast

import testcontainers.core.container
from docker.errors import ImageNotFound
from docker.models.images import Image as DockerImage
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import inside_container


class DockerContainer(testcontainers.core.container.DockerContainer):
    def __init__(self, *args: Any, network: Optional[str] = None, **kwargs: Any) -> None:
        self.network = network or os.getenv("TESTCONTAINER_DOCKER_NETWORK", "bridge")
        super().__init__(*args, **kwargs, network=self.network)

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


class EphemeralDockerImage:
    def __init__(self, dockerfile: pathlib.Path, docker_client_kw: Optional[Dict] = None) -> None:
        self.client = DockerClient(**(docker_client_kw or {}))
        self.image = self.build_image(dockerfile)

    def __enter__(self) -> DockerImage:
        return self.image

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_image()

    def build_image(self, path: pathlib.Path) -> DockerImage:
        if path.is_dir():
            dockerfile_dir = path
            dockerfile_name = ""
        else:
            dockerfile_dir = path.parent
            dockerfile_name = path.name

        image, _ = cast(
            Tuple[DockerImage, Iterator],
            self.client.client.images.build(
                path=str(dockerfile_dir),
                dockerfile=str(dockerfile_name),
                forcerm=True,
            ),
        )
        return image

    def remove_image(self) -> None:
        self.client.client.images.remove(image=str(self.image.id))


def get_docker_image(image_id: str, docker_client_kw: Optional[Dict] = None) -> Optional[DockerImage]:
    client = DockerClient(**(docker_client_kw or {}))
    if not image_id:
        return None
    try:
        return cast(DockerImage, client.client.images.get(image_id))
    except ImageNotFound:
        return None
