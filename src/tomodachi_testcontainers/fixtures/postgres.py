import os
from collections.abc import Generator

import pytest

from tomodachi_testcontainers import DockerContainer, PostgreSQLContainer


@pytest.fixture(scope="session")
def postgres_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("POSTGRES_TESTCONTAINER_IMAGE_ID", "postgres:18")
    disable_logging = bool(os.getenv("POSTGRES_TESTCONTAINER_DISABLE_LOGGING")) or False

    with PostgreSQLContainer(image, disable_logging=disable_logging) as container:
        yield container
