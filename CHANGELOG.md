# Changelog

## 0.14.0-dev (2024-XX-XX)

...

## 0.13.2 (2024-01-09)

### Fixes

- ([#156](https://github.com/filipsnastins/tomodachi-testcontainers/pull/156))
  The `EphemeralDockerImage` and `testcontainers_docker_image` fixture will raise the original error message if the Docker build with BuiltKit fails.
  Previously, the original error was hidden.

## 0.13.1 (2023-12-19)

### New features

- Enable parallel test execution with `pytest-xdist`

### Breaking changes

- Fixture `testcontainers_docker_image` now returns an `image_id` as a `str` instead of `docker.models.images.Image` instance.

## 0.13.0 (2023-12-18)

### New features

- Support Python 3.12

### Fixes

- `DynamoDBAdminContainer`: fix AWS region configuration.

## 0.12.0 (2023-11-26)

### New features

- `TomodachiContainer` - added support for exporting code coverage.
- `TomodachiContainer` - added example of how to attach a remote debugger to the container.

### Documentation

- `README`: documented Testcontainer debugging tips.
- `README`: documented how to export test coverage from `TomodachiContainer`.

### Changes

- `DockerContainer` - logs forwarded from the Testcontainers will exclude timestamps
  to make it easier to read the logs - log lines will be shorter.
- `DockerContainer` - removed `testconatiners-` prefix from the container name
  to make it easier to read the logs - log lines will be shorter.

## 0.11.0 (2023-11-19)

### New features

- Added Minio container - `MinioContainer`
- Added DynamoDB Admin container - `DynamoDBAdminContainer`

### Fixes

- Set `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables on LocalStack container.

## 0.10.4 (2023-11-17)

### New features

- `LocalStackContainer` - updated base image to `localstack/localstack:3`
- `PostgreSQLContainer` - updated base image to `postgres:16`

### Fixes

- `DockerContainer`: remove container if startup failed instead of leaving it in stopped state.
- `MySQLContainer`: add `cryptography` as an extra dependency. Required for `pymysql`.

## 0.10.3 (2023-11-15)

### Fixes

- Fixed a typo in `pyproject` extra dependencies - `pip install tomodachi-testcontainers[mysql]`

## 0.10.2 (2023-11-08)

### New features

- `DockerContainer`: logs from the container are now prefixed with the container name.
  This makes it easier to distinguish logs from multiple containers,
  especially when using multiple containers of the same type.

- `WireMockContainer`: added example of configuring WireMock mappings with [python-wiremock](https://github.com/wiremock/python-wiremock).
  Install [python-wiremock](https://github.com/wiremock/python-wiremock) as an extra dependency with:

  ```bash
  pip install tomodachi-testcontainers[wiremock]
  ```

### Fixes

- `DockerContainer`: forward container logs to the Python logger only when the `DockerContainer` used as a context manager.
  Otherwise, the logger fails in the `DockerContainer.__del__` method, because the logger instance is already closed.

## 0.10.1 (2023-11-06)

### Fixes

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
