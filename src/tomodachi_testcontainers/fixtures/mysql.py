import os
from typing import Generator, cast

import pytest

from .. import MySQLContainer


@pytest.fixture(scope="session")
def mysql_container() -> Generator[MySQLContainer, None, None]:
    image = os.getenv("MYSQL_TESTCONTAINER_IMAGE_ID", "mysql:8")
    with MySQLContainer(image) as container:
        yield cast(MySQLContainer, container)
