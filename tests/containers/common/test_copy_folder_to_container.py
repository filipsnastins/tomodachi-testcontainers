from pathlib import Path
from typing import Generator

import pytest
from docker.models.containers import Container
from testcontainers.core.docker_client import DockerClient

from tomodachi_testcontainers.containers import copy_folder_to_container


@pytest.fixture()
def alpine_container() -> Generator[Container, None, None]:
    client = DockerClient()
    container = client.run("alpine:latest", command="sleep 10", detach=True, remove=True)
    yield container
    container.remove(force=True)


def test_copy_folder_to_container(alpine_container: Container) -> None:
    host_path = Path(__file__).parent / "sample-folder"
    container_path = Path("/tmp")

    copy_folder_to_container(host_path=host_path, container_path=container_path, container=alpine_container)

    code, output = alpine_container.exec_run("find /tmp -type f")
    assert code == 0
    assert set(output.decode("utf-8").strip().split("\n")) == {"/tmp/nested/file-2.txt", "/tmp/file-1.txt"}
    code, output = alpine_container.exec_run("cat /tmp/file-1.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 1\n"
    code, output = alpine_container.exec_run("cat /tmp/nested/file-2.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 2\n"
