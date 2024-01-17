# Configuration Options

!!! note

    Ensure that environment variables are set before running `pytest`, e.g., with [pytest-env](https://pypi.org/project/pytest-env/) plugin.

## General configuration options

| Environment Variable                      | Description                                                                |
| :---------------------------------------- | :------------------------------------------------------------------------- |
| `<CONTAINER-NAME>_TESTCONTAINER_IMAGE_ID` | Override Testcontainer's default Docker Image ID in pytest fixture.        |
| `DOCKER_BUILDKIT`                         | Set `DOCKER_BUILDKIT=1` to use Docker BuildKit for building Docker images. |
| `TESTCONTAINER_DOCKER_NETWORK`            | Launch Testcontainers in specified Docker network. Defaults to `bridge`.   |

### Override Default Docker Image in pytest fixtures

| pytest fixture                                                                 | Default Image              | Image Environment Variable Override |
| :----------------------------------------------------------------------------- | :------------------------- | ----------------------------------: |
| [`testcontainer_image`][tomodachi_testcontainers.pytest.testcontainer_image]   | n/a, built from Dockerfile |            `TESTCONTAINER_IMAGE_ID` |
| [`moto_container`][tomodachi_testcontainers.pytest.moto_container]             | `motoserver/moto:latest`   |       `MOTO_TESTCONTAINER_IMAGE_ID` |
| [`localstack_container`][tomodachi_testcontainers.pytest.localstack_container] | `localstack/localstack:3`  | `LOCALSTACK_TESTCONTAINER_IMAGE_ID` |
| [`minio_container`][tomodachi_testcontainers.pytest.minio_container]           | `minio/minio:latest`       |      `MINIO_TESTCONTAINER_IMAGE_ID` |
| [`sftp_container`][tomodachi_testcontainers.pytest.sftp_container]             | `atmoz/sftp:latest`        |       `SFTP_TESTCONTAINER_IMAGE_ID` |
| [`wiremock_container`][tomodachi_testcontainers.pytest.wiremock_container]     | `wiremock/wiremock:latest` |   `WIREMOCK_TESTCONTAINER_IMAGE_ID` |
| [`mysql_container`][tomodachi_testcontainers.pytest.mysql_container]           | `mysql:8`                  |      `MYSQL_TESTCONTAINER_IMAGE_ID` |
| [`postgres_container`][tomodachi_testcontainers.pytest.postgres_container]     | `postgres:16`              |   `POSTGRES_TESTCONTAINER_IMAGE_ID` |

### Change the default Docker network

By default, Testcontainers are started in the default `bridge` Docker network.
Sometimes, starting containers in a different network is useful, e.g., to isolate parallel test runs.
Specify a new network name with the `TESTCONTAINER_DOCKER_NETWORK` environment variable.
The Docker network is not created automatically, so ensure it exists before running tests.

## [`testcontainer_image`][tomodachi_testcontainers.pytest.testcontainer_image] fixture configuration

| Environment Variable                 | Description                                                |
| :----------------------------------- | :--------------------------------------------------------- |
| `TESTCONTAINER_IMAGE_ID`             | Use given Image ID for creating a container.               |
| `TESTCONTAINER_DOCKERFILE_PATH`      | Override path to the Dockerfile for building Docker image. |
| `TESTCONTAINER_DOCKER_BUILD_CONTEXT` | Override Docker build context.                             |
| `TESTCONTAINER_DOCKER_BUILD_TARGET`  | Override Docker build target.                              |

### Change the Dockerfile path, build context, and build target

If the Dockerfile is not located in the current working directory or you need a different Docker build context,
specify a new path with the `TESTCONTAINER_DOCKERFILE_PATH` and `TESTCONTAINER_DOCKER_BUILD_CONTEXT` environment variables.

Examples:

- `TESTCONTAINER_DOCKERFILE_PATH=examples/Dockerfile.testing`
- `TESTCONTAINER_DOCKER_BUILD_CONTEXT=examples/`

If you have a multi-stage Dockerfile and want to run tests against a specific Docker image stage, specify the stage name
with the `TESTCONTAINER_DOCKER_BUILD_TARGET` environment variable.
Note that it's a best practice to run tests against the release/production stage,
so this environment variable is not needed in most cases, as it's usually the last stage in a Dockerfile.

Example:

- `TESTCONTAINER_DOCKER_BUILD_TARGET=development`

### Run Testcontainer from the pre-built image

If the Testcontainer's Docker image is already built, you can run it in the container
by specifying the Image ID in the `TESTCONTAINER_IMAGE_ID` environment variable.

It is useful for running tests in the deployment pipeline when the image has already been built on the `build` step.
Instead of building a new image from scratch for the tests, we want to test the same image that
will be pushed to a Container Registry and deployed to production.

Examples:

- `TESTCONTAINER_IMAGE_ID=sha256:56ca9586de1cf25081bb5f070b59b86625b6221bb26d7409a74e6051d7954c92`
- `TESTCONTAINER_IMAGE_ID=mycompany/my-application:1.0.0`

## Included Testcontainers configuration

Testcontainer configuration can be changed by setting these environment variables on a _host machine_.
It's handy when you want to change the default configuration of Testcontianers when using their [pytest fixtures](./reference/pytest/fixtures.md).

- [`LocalStackContainer`][tomodachi_testcontainers.LocalStackContainer]

      - `AWS_REGION` or `AWS_DEFAULT_REGION` - defaults to `us-east-1`
      - `AWS_ACCESS_KEY_ID` - defaults to `testing`
      - `AWS_SECRET_ACCESS_KEY` - defaults to `testing`

- [`MototContainer`][tomodachi_testcontainers.MotoContainer]

      - `AWS_REGION` or `AWS_DEFAULT_REGION` - defaults to `us-east-1`
      - `AWS_ACCESS_KEY_ID` - defaults to `testing`
      - `AWS_SECRET_ACCESS_KEY` - defaults to `testing`

- [`MinioContainer`][tomodachi_testcontainers.MinioContainer]

      - `AWS_REGION` or `AWS_DEFAULT_REGION` - defaults to `us-east-1`
      - `MINIO_ROOT_USER` - defaults to `minioadmin`
      - `MINIO_ROOT_PASSWORD` - defaults to `minioadmin`

- [`MySQLContainer`][tomodachi_testcontainers.MySQLContainer]

      - `MYSQL_DRIVERNAME` - defaults to `mysql+pymysql`
      - `MYSQL_USER` - defaults to `username`
      - `MYSQL_ROOT_PASSWORD` - defaults to `root`
      - `MYSQL_PASSWORD` - defaults to `password`
      - `MYSQL_DATABASE` - defaults to `db`

- [`PostgreSQLContainer`][tomodachi_testcontainers.PostgreSQLContainer]

      - `POSTGRES_DRIVERNAME` - defaults to `postgresql+psycopg2`
      - `POSTGRES_USER` - defaults to `username`
      - `POSTGRES_PASSWORD` - defaults to `password`
      - `POSTGRES_DB` - defaults to `db`

- [`TomodachiContainer`][tomodachi_testcontainers.TomodachiContainer]

      - `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE` - defaults to `False`

- [`WireMockContainer`][tomodachi_testcontainers.WireMockContainer]

      - `WIREMOCK_TESTCONTAINER_MAPPING_STUBS` - path to WireMock mapping stubs, defaults to `None`
      - `WIREMOCK_TESTCONTAINER_MAPPING_FILES` - path to WireMock mapping files, defaults to `None`
      - `WIREMOCK_TESTCONTAINER_VERBOSE` - set to `1` to start WireMock in verbose mode, defaults to `None`
