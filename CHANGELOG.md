# Changelog

## 1.2.4 (2025-02-16)

### Maintenance

- Updates testcontainers to [`4.9.1`](https://github.com/testcontainers/testcontainers-python/releases/tag/testcontainers-v4.9.1).
- Removes custom implementation of `DockerContainer.get_container_host_ip`
  in favour of fixed implementation in `testcontainers.core.container.DockerContainer` base class.
- Dependency updates.

### Maintenance

## 1.2.3 (2024-10-19)

### Maintenance

- Updates [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) to [0.24.0](https://github.com/pytest-dev/pytest-asyncio/releases/tag/v0.24.0).
  Using `'loop_scope="session"`.
- Dependency updates.

## 1.2.2 (2024-07-16)

### Maintenance

- Development scripts moved from the Poetry scripts to Makefile.
  Unnecessary development scripts are no longer packaged as part of the library.
- Dependency updates.
- Extended `pylint` config and added `pydocstringformatter` linter.

## 1.2.1 (2024-05-14)

### Maintenance

- ([#306](https://github.com/filipsnastins/tomodachi-testcontainers/pull/306))
  Bump `[testcontainers-python](https://github.com/testcontainers/testcontainers-python)` to `4.4.1`.

## 1.2.0 (2024-05-14)

### New features

- ([#305](https://github.com/filipsnastins/tomodachi-testcontainers/pull/305))
  Adds `<CONTAINER-NAME>_TESTCONTAINER_DISABLE_LOGGING` environment variable
  to selectively disable logging capture and forwarding for specific containers.
  The use case is that some containers, like Moto, output logs that are not immediately useful for debugging.
  Example usage: `MOTO_TESTCONTAINER_DISABLE_LOGGING=1`.

## 1.1.3 (2024-05-06)

### Maintenance

- Bump pytest-asyncio to [0.21.2](https://github.com/pytest-dev/pytest-asyncio/releases/tag/v0.21.2) to resolve the compatibility issue with pytest 8.2.0.

## 1.1.2 (2024-03-09)

### Maintenance

- ([#242](https://github.com/filipsnastins/tomodachi-testcontainers/pull/242))
  Drop Python 3.8 support.
- ([#242](https://github.com/filipsnastins/tomodachi-testcontainers/pull/242))
  Update [testcontainers-python](https://github.com/testcontainers/testcontainers-python) to `4.0.0`.

## 1.1.1 (2024-02-29)

### New features

- ([#234](https://github.com/filipsnastins/tomodachi-testcontainers/pull/234))
  `clients.SNSSQSTestClient`: supports SQS messaging introduced in tomodachi [0.27](https://github.com/kalaspuff/tomodachi/releases/tag/0.27.0).

## 1.1.0 (2024-01-25)

### New features

- ([#180](https://github.com/filipsnastins/tomodachi-testcontainers/pull/180))
  `clients.SNSSQSTestClient`: `SNSSQSTestClient.receive` now returns message attributes.
  The returned message is now wrapped in a `SQSMessage` dataclass, containing the `payload` and `message_attributes` fields.
  It's a small breaking change for clients that use the `receive` method, because the message's payload is now wrapped in the `payload` attribute.

## 1.0.1 (2024-01-23)

### Fixes

- ([#179](https://github.com/filipsnastins/tomodachi-testcontainers/pull/179))
  `WireMockContainer`: fixed `mapping_stubs` and `mapping_files` argument precedence over environment variables.

## 1.0.0 (2024-01-20) 🎉

### New features

- New documentation available at <https://filipsnastins.github.io/tomodachi-testcontainers/>

- `WireMockContainer`: adds `wiremock_container` pytest fixture.

- `WireMockContainer`: adds `reset_wiremock_container_on_teardown` pytest fixture that deletes all WireMock stub mappings after each test.

- `edge_port` in all Testcontainers now defaults to `None`.
  When it's `None`, the container will be started with a random port generated by `tomodachi_testcontainers.utils.get_available_port()`.

- `tomodachi_testcontainers.pytest` module removed, and the code moved one level up:

  - `tomodachi_testcontainers.fixtures`
  - `tomodachi_testcontainers.assertions`
  - `tomodachi_testcontainers.async_probes`

### Breaking changes

- Removed the leading underscore from `restart_localstack_container_on_teardown` and `reset_moto_container_on_teardown` pytest fixture names.

- Fixtures `moto_snssqs_tc` and `localstack_snssqs_tc` are now session-scoped (`@pytest.fixture(scope="session")`).

- Fixture `testcontainers_docker_image` renamed to `testcontainer_image`.

- Renamed environment variables:

  | Old name                                       | New name                             |
  | :--------------------------------------------- | :----------------------------------- |
  | `TOMODACHI_TESTCONTAINER_DOCKER_NETWORK`       | `TESTCONTAINER_DOCKER_NETWORK`       |
  | `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH`      | `TESTCONTAINER_DOCKERFILE_PATH`      |
  | `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT` | `TESTCONTAINER_DOCKER_BUILD_CONTEXT` |
  | `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET`  | `TESTCONTAINER_DOCKER_BUILD_TARGET`  |
  | `TOMODACHI_TESTCONTAINER_IMAGE_ID`             | `TESTCONTAINER_IMAGE_ID`             |

## 0.14.0 (2024-01-18)

### New features

- ([#169](https://github.com/filipsnastins/tomodachi-testcontainers/pull/169))
  `clients.SNSSQSTestClient`: new `send` method for sending messages to SQS queues.

### Breaking changes

- ([#169](https://github.com/filipsnastins/tomodachi-testcontainers/pull/169))
  `clients.SNSSQSTestClient`: removed redundant `fifo` argument from `create_queue`, `create_topic`, and `subscribe_to` method;
  relying on the `queue_name` and `topic_name` to end with `.fifo` suffix instead.

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
