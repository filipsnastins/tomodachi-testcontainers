from pathlib import Path
from typing import Generator, cast

import pytest

from tomodachi_testcontainers.containers import copy_folder_to_container
from tomodachi_testcontainers.containers import DockerContainer


class AlpineContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="alpine:latest")


@pytest.fixture()
def alpine_container() -> Generator[AlpineContainer, None, None]:
    with AlpineContainer().with_command("sleep 10") as container:
        yield cast(AlpineContainer, container)


def test_copy_folder_to_container(alpine_container: AlpineContainer) -> None:
    host_path = Path(__file__).parent / "sample-folder"
    container_path = Path("/tmp")

    copy_folder_to_container(
        host_path=host_path, container_path=container_path, container=alpine_container.get_wrapped_container()
    )

    code, output = alpine_container.exec("find /tmp -type f")
    assert code == 0
    assert set(output.decode("utf-8").strip().split("\n")) == {"/tmp/nested/file-2.txt", "/tmp/file-1.txt"}
    code, output = alpine_container.exec("cat /tmp/file-1.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 1\n"
    code, output = alpine_container.exec("cat /tmp/nested/file-2.txt")
    assert code == 0
    assert output.decode("utf-8") == "file 2\n"
