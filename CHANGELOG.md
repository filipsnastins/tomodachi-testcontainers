# Changelog

## 0.10.1 (2023-11-06)

### Bug fixes

- `import tomodachi_testcontainers.pytest` was failing with `ImportError` because `MySQL` and `PostgreSQL` fixtures were not
  handled as optional imports.

## 0.10.0 (2023-11-05)

### New features

- ([#90](https://github.com/filipsnastins/tomodachi-testcontainers/pull/90))
  `DockerContainer`:
  added abstract method `log_message_on_container_start`
  which returns a string that is logged when the container starts.
  It's useful for providing an information message of how to use the test container.
  For example, in case of `MotoContainer`,
  it outputs a link to the [Moto Dashboard](https://docs.getmoto.org/en/latest/docs/server_mode.html#dashboard).

- ([#90](https://github.com/filipsnastins/tomodachi-testcontainers/pull/90))
  `clients.snssqs`:
  added cache for storing topic/queue ARNs and URLs to reduce amount of API calls to AWS
- ([#90](https://github.com/filipsnastins/tomodachi-testcontainers/pull/90))
  `clients.snssqs`:
  added new methods for fetching topic/queue attributes:
  - `get_topic_arn`
  - `get_topic_attributes`
  - `get_queue_arn`
  - `get_queue_url`
  - `get_queue_attributes`
- ([#90](https://github.com/filipsnastins/tomodachi-testcontainers/pull/90))
  `clients.snssqs`:
  added `purge_queue` method

- ([#92](https://github.com/filipsnastins/tomodachi-testcontainers/pull/92))
  Added abstract `DatabaseContainer` and `WebContainer`

- ([#92](https://github.com/filipsnastins/tomodachi-testcontainers/pull/92))
  Added `MySQLContainer`

  - Install with:

    ```bash
      # DatabaseContainer and SQLAlchemy
      pip install tomodachi-testcontainers[db]

      # MySQLContainer, SQLAlchemy and pymysql
      pip install tomodachi-testcontainers[mysql]
    ```

- ([#94](https://github.com/filipsnastins/tomodachi-testcontainers/pull/94))
  Added `PostgreSQLContainer`

  - Install with:

    ```bash
      # DatabaseContainer and SQLAlchemy
      pip install tomodachi-testcontainers[db]

      # PostgreSQLContainer, SQLAlchemy and psycopg2
      pip install tomodachi-testcontainers[postgres]
    ```

### Breaking changes

- ([#91](https://github.com/filipsnastins/tomodachi-testcontainers/pull/91))
  `DockerContainer.restart_container` method renamed to `DockerContainer.restart`

- ([#92](https://github.com/filipsnastins/tomodachi-testcontainers/pull/92))
  `tomodachi_testcontainers.utils.wait_for_http_healthcheck` moved to `tomodachi_testcontainers.containers.common.web`
