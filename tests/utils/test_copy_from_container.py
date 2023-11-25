from pathlib import Path
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import DockerContainer
from tomodachi_testcontainers.utils import copy_from_container


class AlpineContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="alpine:latest")

    def log_message_on_container_start(self) -> str:
        return "Alpine container started"


@pytest.fixture(scope="module")
def alpine_container() -> Generator[AlpineContainer, None, None]:
    with AlpineContainer().with_command("sleep infinity") as container:
        yield cast(AlpineContainer, container)


def test_copy_from_container(alpine_container: AlpineContainer, tmpdir: Path) -> None:
    alpine_container.exec("mkdir -p /tmp/dir-1")
    alpine_container.exec("sh -c 'echo file 1 > /tmp/dir-1/file-1.txt'")
    alpine_container.exec("sh -c 'echo file 2 > /tmp/dir-1/file-2.txt'")

    copy_from_container(alpine_container.get_wrapped_container(), container_path=Path("/tmp/dir-1"), host_path=tmpdir)

    assert (tmpdir / "dir-1" / "file-1.txt").read_text(encoding="utf-8") == "file 1\n"
    assert (tmpdir / "dir-1" / "file-2.txt").read_text(encoding="utf-8") == "file 2\n"
