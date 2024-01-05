# Configuration Options

## Configuration with environment variables

⚠️ Make sure that environment variables are set before running `pytest` -
e.g. with [pytest-env](https://pypi.org/project/pytest-env/) plugin or
by setting it in the shell before running `pytest`.

| Environment Variable                           | Description                                                                                                 |
| :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `<CONTAINER-NAME>_TESTCONTAINER_IMAGE_ID`      | Override any supported Testcontainer Image ID. Defaults to `None`                                           |
| `DOCKER_BUILDKIT`                              | Set `DOCKER_BUILDKIT=1` to use Docker BuildKit for building Docker images                                   |
| `TESTCONTAINER_DOCKER_NETWORK`                 | Launch testcontainers in specified Docker network. Defaults to 'bridge'. Network must be created beforehand |
| `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH`      | Override path to Dockerfile for building Tomodachi service image. (`--file` flag in `docker build` command) |
| `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT` | Override Docker build context                                                                               |
| `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET`  | Override Docker build target (`--target` flag in `docker build` command)                                    |
| `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE`      | Set `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1` to export `.coverage` file when the container stops.        |

## Change Dockerfile path, build context and build target

If the Dockerfile is not located in the current working directory or you need a different Docker build context,
specify a new path with the `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH` and `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT`
environment variables.

Examples:

- `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH=examples/Dockerfile.testing`
- `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT=examples/`

If you have a multi-stage Dockerfile and want to run testcontainer tests against a specific stage, specify the stage name
with the `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET` environment variable.
Note that usually want to run tests against the release/production stage, so this environment variable is not needed in most cases,
as it's the last stage in the Dockerfile.

Example:

- `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET=development`

## Change the default Docker network

By default, Testcontainers are started in the default `bridge` Docker network.
Sometimes it's useful to start containers in a different network, e.g. a network
specifically dedicated for running automated tests.

Specify a new network name with the `TOMODACHI_TESTCONTAINER_NETWORK` environment variable.
The Docker network is not created automatically, so make sure that it exists before running tests.

⚠️ Make sure that the environment variable is set before running `pytest`.

## Run Testcontainer from the pre-built image

If the Tomodachi service Docker image is already built, you can run the container
by specifying the image ID in the `TOMODACHI_TESTCONTAINER_IMAGE_ID` environment variable.

It is useful when running tests in the deployment pipeline when the image has been already built on the build step.
Instead of building a new image from scratch for the tests, we want to test the exact same image that
will be pushed to a Container Registry and deployed to production.

Examples:

- `TOMODACHI_TESTCONTAINER_IMAGE_ID=sha256:56ca9586de1cf25081bb5f070b59b86625b6221bb26d7409a74e6051d7954c92`
- `TOMODACHI_TESTCONTAINER_IMAGE_ID=mycompany/my-tomodachi-application:1.0.0`

⚠️ Make sure that the environment variable is set before running `pytest`.

## Override Testcontainers Docker Image

| Container Name | Default Image              |              Image Env Var Override |
| :------------- | :------------------------- | ----------------------------------: |
| Moto           | `motoserver/moto:latest`   |       `MOTO_TESTCONTAINER_IMAGE_ID` |
| LocalStack     | `localstack/localstack:3`  | `LOCALSTACK_TESTCONTAINER_IMAGE_ID` |
| Minio          | `minio/minio:latest`       |      `MINIO_TESTCONTAINER_IMAGE_ID` |
| SFTP           | `atmoz/sftp:latest`        |       `SFTP_TESTCONTAINER_IMAGE_ID` |
| WireMock       | `wiremock/wiremock:latest` |   `WIREMOCK_TESTCONTAINER_IMAGE_ID` |
| MySQL          | `mysql:8`                  |      `MYSQL_TESTCONTAINER_IMAGE_ID` |
| PostgreSQL     | `postgres:16`              |   `POSTGRES_TESTCONTAINER_IMAGE_ID` |
