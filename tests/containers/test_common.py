import tempfile
from pathlib import Path
from typing import Generator

import pytest
from docker.errors import BuildError, ImageNotFound

from tomodachi_testcontainers.containers import EphemeralDockerImage, get_docker_image


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

    def test_build_docker_image_and_remove_on_cleanup(
        self, dockerfile_hello_world: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("DOCKER_BUILDKIT", raising=False)

        with EphemeralDockerImage(dockerfile_hello_world) as image:
            assert get_docker_image(image_id=str(image.id))

        with pytest.raises(ImageNotFound):
            get_docker_image(image_id=str(image.id))

    def test_build_with_docker_buildkit(self, dockerfile_buildkit: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DOCKER_BUILDKIT", "1")

        with EphemeralDockerImage(dockerfile_buildkit) as image:
            assert get_docker_image(image_id=str(image.id))

    def test_build_error_when_docker_buildkit_envvar_not_set(
        self, dockerfile_buildkit: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("DOCKER_BUILDKIT", raising=False)

        with pytest.raises(BuildError), EphemeralDockerImage(dockerfile_buildkit):
            pass
