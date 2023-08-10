import tempfile
from pathlib import Path
from typing import Generator

import pytest
from docker.errors import BuildError, ImageNotFound
from docker.models.containers import Container
from testcontainers.core.docker_client import DockerClient

from tomodachi_testcontainers.containers import EphemeralDockerImage, copy_folder_to_container, get_docker_image


@pytest.fixture()
def alpine_container() -> Generator[Container, None, None]:
    client = DockerClient()
    container = client.run("alpine:latest", command="sleep 10", detach=True, remove=True)
    yield container
    container.remove(force=True)


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


def test_copy_folder_to_container(alpine_container: Container) -> None:
    host_path = Path(__file__).parent / "sample-folder"
    container_path = Path("/tmp")

    copy_folder_to_container(host_path=host_path, container_path=container_path, container=alpine_container)

    code, output = alpine_container.exec_run("find /tmp -type f")
    assert code == 0
    assert output.decode("utf-8") == "/tmp/file-1.txt\n/tmp/file-2.txt\n"
    code, output = alpine_container.exec_run("cat /tmp/file-1.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 1"
    code, output = alpine_container.exec_run("cat /tmp/file-2.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 2"
