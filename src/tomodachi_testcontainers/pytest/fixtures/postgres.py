import os
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import PostgreSQLContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgreSQLContainer, None, None]:
    image = os.getenv("POSTGRES_TESTCONTAINER_IMAGE_ID", "postgres:16")
    with PostgreSQLContainer(image=image, edge_port=get_available_port()) as container:
        yield cast(PostgreSQLContainer, container)
