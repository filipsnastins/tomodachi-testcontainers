from pathlib import Path

from tests.conftest import AlpineContainer
from tomodachi_testcontainers.utils import copy_folder_to_container


def test_copy_folder_to_container(alpine_container: AlpineContainer) -> None:
    host_path = Path(__file__).parent / "sample-folder"
    container_path = Path("/tmp")

    copy_folder_to_container(
        alpine_container.get_wrapped_container(), host_path=host_path, container_path=container_path
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
