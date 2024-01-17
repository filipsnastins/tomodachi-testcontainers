import os
from typing import Generator, cast

import pytest

from .. import PostgreSQLContainer


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgreSQLContainer, None, None]:
    image = os.getenv("POSTGRES_TESTCONTAINER_IMAGE_ID", "postgres:16")
    with PostgreSQLContainer(image) as container:
        yield cast(PostgreSQLContainer, container)
