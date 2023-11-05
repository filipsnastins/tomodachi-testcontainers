import pytest
from sqlalchemy.exc import OperationalError

from tomodachi_testcontainers.containers.database import DatabaseURL, wait_for_database_healthcheck
from tomodachi_testcontainers.containers.mysql import MySQLContainer
from tomodachi_testcontainers.utils import get_available_port


def test_no_connection_to_host() -> None:
    url = DatabaseURL(
        drivername="mysql+pymysql",
        username="root",
        password="root",
        host="localhost",
        port=get_available_port(),
        database="test",
    )
    with pytest.raises(OperationalError):
        wait_for_database_healthcheck(url, timeout=1.0)


def test_healthcheck_passes(mysql_container: MySQLContainer) -> None:
    wait_for_database_healthcheck(mysql_container.get_external_url(), timeout=1.0)
