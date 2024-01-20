# Installation

Install with [pip](https://pip.pypa.io/en/stable/getting-started/):

```sh
pip install tomodachi-testcontainers
```

Install with [Poetry](https://python-poetry.org/):

```sh
poetry add --group dev tomodachi-testcontainers
```

Extra packages:

```sh
# Generic DatabaseContainer and SQLAlchemy
pip install tomodachi-testcontainers[db]

# MySQLContainer, SQLAlchemy and pymysql
pip install tomodachi-testcontainers[mysql]

# PostgreSQLContainer, SQLAlchemy and psycopg2
pip install tomodachi-testcontainers[postgres]

# SFTPContainer and asyncssh
pip install tomodachi-testcontainers[sftp]

# Installs python-wiremock SDK
pip install tomodachi-testcontainers[wiremock]
```
