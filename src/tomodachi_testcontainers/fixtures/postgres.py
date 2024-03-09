import os
from typing import Generator

import pytest

from tomodachi_testcontainers import DockerContainer

from .. import PostgreSQLContainer


@pytest.fixture(scope="session")
def postgres_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("POSTGRES_TESTCONTAINER_IMAGE_ID", "postgres:16")
    with PostgreSQLContainer(image) as container:
        yield container
