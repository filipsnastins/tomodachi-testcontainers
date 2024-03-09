import os
from typing import Generator

import pytest

from .. import DockerContainer, MySQLContainer


@pytest.fixture(scope="session")
def mysql_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("MYSQL_TESTCONTAINER_IMAGE_ID", "mysql:8")
    with MySQLContainer(image) as container:
        yield container
