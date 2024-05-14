import os
from typing import Generator

import pytest

from .. import DockerContainer, MySQLContainer


@pytest.fixture(scope="session")
def mysql_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("MYSQL_TESTCONTAINER_IMAGE_ID", "mysql:8")
    disable_logging = bool(os.getenv("MYSQL_TESTCONTAINER_DISABLE_LOGGING", False))

    with MySQLContainer(image, disable_logging=disable_logging) as container:
        yield container
