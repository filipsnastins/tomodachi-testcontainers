import sqlalchemy

from tomodachi_testcontainers import PostgreSQLContainer


def test_postgres_container_starts(postgres_container: PostgreSQLContainer) -> None:
    url = postgres_container.get_external_url()
    engine = sqlalchemy.create_engine(url.to_str())

    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT version();"))

    assert "PostgreSQL" in str(result.scalar())
