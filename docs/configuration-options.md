# Configuration Options

!!! note

    Ensure that environment variables are set before running `pytest`, e.g., with [pytest-env](https://pypi.org/project/pytest-env/) plugin.

## General configuration options

| Environment Variable                      | Description                                                                |
| :---------------------------------------- | :------------------------------------------------------------------------- |
| `<CONTAINER-NAME>_TESTCONTAINER_IMAGE_ID` | Override supported Testcontainer default Docker Image ID.                  |
| `DOCKER_BUILDKIT`                         | Set `DOCKER_BUILDKIT=1` to use Docker BuildKit for building Docker images. |
| `TESTCONTAINER_DOCKER_NETWORK`            | Launch Testcontainers in specified Docker network. Defaults to `bridge`.   |

### Override Default Docker Image

| Container Name                                                        | Default Image              | Image Environment Variable Override |
| :-------------------------------------------------------------------- | :------------------------- | ----------------------------------: |
| [`MotoContainer`][tomodachi_testcontainers.MotoContainer]             | `motoserver/moto:latest`   |       `MOTO_TESTCONTAINER_IMAGE_ID` |
| [`LocalStackContainer`][tomodachi_testcontainers.LocalStackContainer] | `localstack/localstack:3`  | `LOCALSTACK_TESTCONTAINER_IMAGE_ID` |
| [`MinioContainer`][tomodachi_testcontainers.MinioContainer]           | `minio/minio:latest`       |      `MINIO_TESTCONTAINER_IMAGE_ID` |
| [`SFTPContainer`][tomodachi_testcontainers.SFTPContainer]             | `atmoz/sftp:latest`        |       `SFTP_TESTCONTAINER_IMAGE_ID` |
| [`WireMockContainer`][tomodachi_testcontainers.WireMockContainer]     | `wiremock/wiremock:latest` |   `WIREMOCK_TESTCONTAINER_IMAGE_ID` |
| [`MySQLContainer`][tomodachi_testcontainers.MySQLContainer]           | `mysql:8`                  |      `MYSQL_TESTCONTAINER_IMAGE_ID` |
| [`PostgreSQLContainer`][tomodachi_testcontainers.PostgreSQLContainer] | `postgres:16`              |   `POSTGRES_TESTCONTAINER_IMAGE_ID` |

### Change the default Docker network

By default, Testcontainers are started in the default `bridge` Docker network.
Sometimes, starting containers in a different network is useful, e.g., to isolate parallel test runs.
Specify a new network name with the `TESTCONTAINER_DOCKER_NETWORK` environment variable.
The Docker network is not created automatically, so ensure it exists before running tests.

## [`testcontainer_image`][tomodachi_testcontainers.pytest.testcontainer_image] fixture configuration

| Environment Variable                 | Description                                                |
| :----------------------------------- | :--------------------------------------------------------- |
| `TESTCONTAINER_DOCKERFILE_PATH`      | Override path to the Dockerfile for building Docker image. |
| `TESTCONTAINER_DOCKER_BUILD_CONTEXT` | Override Docker build context.                             |
| `TESTCONTAINER_DOCKER_BUILD_TARGET`  | Override Docker build target.                              |
| `TESTCONTAINER_IMAGE_ID`             | Use given Image ID for creating a container.               |

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

TODO
