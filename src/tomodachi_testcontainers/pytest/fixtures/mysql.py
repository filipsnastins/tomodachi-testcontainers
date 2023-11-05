import os
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import MySQLContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def mysql_container() -> Generator[MySQLContainer, None, None]:
    image = os.getenv("MYSQL_TESTCONTAINER_IMAGE_ID", "mysql:8")
    with MySQLContainer(image=image, edge_port=get_available_port()) as container:
        yield cast(MySQLContainer, container)
