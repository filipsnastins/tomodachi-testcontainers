import tempfile
from pathlib import Path
from typing import Generator

import docker
import pytest
from docker.errors import BuildError, ImageNotFound

from tomodachi_testcontainers.containers.common import EphemeralDockerImage


class TestEphemeralDockerImage:
    @pytest.fixture()
    def dockerfile_hello_world(self, tmp_path: Path) -> Generator[Path, None, None]:
        with tempfile.NamedTemporaryFile(mode="wt", encoding="utf-8", dir=tmp_path) as dockerfile:
            dockerfile.writelines(
                [
                    "FROM alpine:latest\n",
                    "RUN echo 'Hello, world!'\n",
                ]
            )
            dockerfile.flush()
            yield Path(dockerfile.name)

    @pytest.fixture()
    def dockerfile_buildkit(self, tmp_path: Path) -> Generator[Path, None, None]:
        with tempfile.NamedTemporaryFile(mode="wt", encoding="utf-8", dir=tmp_path) as dockerfile:
            dockerfile.writelines(
                [
                    "FROM alpine:latest\n",
                    # -- mount is a buildkit feature
                    "RUN --mount=type=secret,id=test,target=test echo 'Hello, World!'\n",
                ]
            )
            dockerfile.flush()
            yield Path(dockerfile.name)

    def test_build_docker_image_and_remove_on_cleanup(self, dockerfile_hello_world: Path) -> None:
        client = docker.from_env()

        with EphemeralDockerImage(dockerfile_hello_world) as image:
            assert client.images.get(image.id)

        with pytest.raises(ImageNotFound):
            client.images.get(image.id)

    def test_build_with_docker_buildkit(self, dockerfile_buildkit: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DOCKER_BUILDKIT", "1")
        client = docker.from_env()

        with EphemeralDockerImage(dockerfile_buildkit) as image:
            assert client.images.get(image.id)

    def test_build_error_when_docker_buildkit_envvar_not_set(self, dockerfile_buildkit: Path) -> None:
        with pytest.raises(BuildError), EphemeralDockerImage(dockerfile_buildkit):
            pass
