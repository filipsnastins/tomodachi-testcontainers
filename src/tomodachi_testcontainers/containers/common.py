import pathlib
from typing import Any, Dict, Iterator, Optional, Tuple, cast

from docker.errors import ImageNotFound
from docker.models.images import Image as DockerImage
from testcontainers.core.docker_client import DockerClient


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
