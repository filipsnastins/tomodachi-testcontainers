import sqlalchemy

from tomodachi_testcontainers import MySQLContainer


def test_mysql_container_starts(mysql_container: MySQLContainer) -> None:
    url = mysql_container.get_external_url()
    engine = sqlalchemy.create_engine(url.to_str())

    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))

    assert result.scalar() == 1
