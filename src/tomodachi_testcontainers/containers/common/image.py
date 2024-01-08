import os
import subprocess  # nosec: B404
from pathlib import Path
from types import TracebackType
from typing import Dict, Iterator, Optional, Tuple, Type, cast

from docker.errors import BuildError
from docker.models.images import Image
from testcontainers.core.docker_client import DockerClient


class EphemeralDockerImage:
    """Builds a Docker image from a given Dockerfile and removes it when the context manager exits."""

    image: Image

    def __init__(
        self,
        dockerfile: Optional[Path] = None,
        context: Optional[Path] = None,
        target: Optional[str] = None,
        docker_client_kwargs: Optional[Dict] = None,
        *,
        remove_image_on_exit: bool = True,
    ) -> None:
        self.dockerfile = str(dockerfile) if dockerfile else None
        self.context = str(context) if context else "."
        self.target = target
        self._docker_client = DockerClient(**(docker_client_kwargs or {}))
        self._remove_image_on_exit = remove_image_on_exit

    def __enter__(self) -> Image:
        return self._build_image()

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        if self._remove_image_on_exit:
            self._remove_image()

    def _build_image(self) -> Image:
        if os.getenv("DOCKER_BUILDKIT"):
            self.image = self._build_with_docker_buildkit_cli()
        else:
            self.image = self._build_with_docker_client()
        return self.image

    def _remove_image(self) -> None:
        self._docker_client.client.images.remove(image=str(self.image.id))

    def _build_with_docker_buildkit_cli(self) -> Image:
        cmd = ["docker", "build", "-q", "--rm=true"]
        if self.dockerfile:
            cmd.extend(["-f", self.dockerfile])
        if self.target:
            cmd.extend(["--target", self.target])
        cmd.append(self.context)

        try:
            result = subprocess.run(  # nosec: B603
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf-8")
            raise BuildError(f"Failed to build image with Docker BuildKit: {stderr}", stderr) from e
        image_id = result.stdout.decode("utf-8").strip()
        return cast(Image, self._docker_client.client.images.get(image_id))

    def _build_with_docker_client(self) -> Image:
        image, _ = cast(
            Tuple[Image, Iterator],
            self._docker_client.client.images.build(
                dockerfile=self.dockerfile,
                path=self.context,
                target=self.target,
                forcerm=True,
            ),
        )
        return image
