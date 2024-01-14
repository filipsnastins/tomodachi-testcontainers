from typing import Generator, cast

import pytest
from testcontainers.core.container import DockerContainer


class AlpineContainer(DockerContainer):
    def __init__(self) -> None:
        super().__init__(image="alpine:latest")


@pytest.fixture(scope="session")
def alpine_container() -> Generator[AlpineContainer, None, None]:
    with AlpineContainer().with_command("sleep infinity") as container:
        yield cast(AlpineContainer, container)


def test_alpine_container(alpine_container: AlpineContainer) -> None:
    code, _ = alpine_container.exec("sh -c \"echo 'Hello from Alpine' > /tmp/hello.txt\"")
    assert code == 0

    code, output = alpine_container.exec("sh -c 'cat /tmp/hello.txt'")

    assert code == 0
    assert bytes(output).decode("utf-8") == "Hello from Alpine\n"
