# tomodachi-testcontainers

The library provides [Testcontainers](src/tomodachi_testcontainers/containers/),
[Pytest fixtures](src/tomodachi_testcontainers/pytest/),
and [test clients](src/tomodachi_testcontainers/clients/) for working with Testcontainers,
and testing applications built with [Python Tomodachi framework](https://github.com/kalaspuff/tomodachi).

This library has been created to explore and learn Testcontainers.

Although it has been intended to be used with the Tomodachi framework,
it can be adapted to work with any Python or non-Python framework.

It's built on top of [testcontainers-python](https://github.com/testcontainers/testcontainers-python) library.

[Testcontainers](https://testcontainers.com/) is an open-source framework for providing throwaway,
lightweight instances of databases, message brokers, web browsers,
or just about anything that can run in a Docker container.
It facilitates the use of Docker containers for functional, integration, and end-to-end testing.

- [tomodachi-testcontainers](#tomodachi-testcontainers)
  - [Installation](#installation)
  - [Quickstart and examples](#quickstart-and-examples)
  - [Getting started](#getting-started)
    - [Testing standalone Tomodachi service](#testing-standalone-tomodachi-service)
    - [Change Dockerfile path, build context and build target](#change-dockerfile-path-build-context-and-build-target)
    - [Running Tomodachi container from pre-built image](#running-tomodachi-container-from-pre-built-image)
    - [Testing Tomodachi service with external dependencies](#testing-tomodachi-service-with-external-dependencies)
  - [Benefits and dangers of end-to-end tests](#benefits-and-dangers-of-end-to-end-tests)
    - [Building confidence of releasability](#building-confidence-of-releasability)
    - [⚠️ Mind the Test Pyramid - don't overdo end-to-end tests](#️-mind-the-test-pyramid---dont-overdo-end-to-end-tests)
  - [Running Testcontainers in CI pipeline](#running-testcontainers-in-ci-pipeline)
  - [Supported Testcontainers](#supported-testcontainers)
    - [Tomodachi](#tomodachi)
    - [Moto](#moto)
    - [LocalStack](#localstack)
    - [SFTP](#sftp)
    - [WireMock](#wiremock)
  - [Configuration with environment variables](#configuration-with-environment-variables)
  - [Change default Docker network](#change-default-docker-network)
  - [Forward Testcontainer logs to Pytest](#forward-testcontainer-logs-to-pytest)
  - [Resources and acknowledgements](#resources-and-acknowledgements)
  - [Development](#development)

## Installation

```bash
pip install tomodachi-testcontainers

# Extra dependency - SFTP container and asyncssh
pip install tomodachi-testcontainers[sftp]
```

## Quickstart and examples

Tomodachi service examples are in [examples/](examples/) folder. Their end-to-end tests are in [tests/test_services](tests/test_services).

For full list of available testcontainers, check out [Supported Testcontainers](#supported-testcontainers) section,
[tomodachi_testcontainers.containers](src/tomodachi_testcontainers/containers/) module,
and the official [testcontainers-python](https://github.com/testcontainers/testcontainers-python) library -
it makes it easy to create your own Testcontainers.

For full list of available Pytest fixtures check out [tomodachi_testcontainers.pytest](src/tomodachi_testcontainers/pytest/) module,
and for test clients - [tomodachi_testcontainers.clients](src/tomodachi_testcontainers/clients/) module.

## Getting started

### Testing standalone Tomodachi service

Starting with a simple service that returns `HTTP 200` on the `GET /health` endpoint.

We'd like to test that the service is working.
To do that, we'll package the application as a Docker image, run the container,
send some requests, and assert the responses.

The example assumes that a Dockerfile for running the service is present in the
current working directory. An [example Dockerfile](examples/Dockerfile) is in the [examples/](examples/).

```python
import tomodachi
from aiohttp import web


class TomodachiServiceHealthcheck(tomodachi.Service):
    name = "service-healthcheck"

    @tomodachi.http("GET", r"/health/?")
        async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})
```

The following `tomodachi_container` fixture builds and runs the service as a Docker container.

```python
from typing import Generator, cast

import pytest
from docker.models.images import Image

from tomodachi_testcontainers.containers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def tomodachi_container(tomodachi_image: Image) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=str(tomodachi_image.id),
        edge_port=get_available_port(),
    ) as container:
        yield cast(TomodachiContainer, container)
```

The `tomodachi_image` fixture is from the `tomodachi_testcontainers` library.
It builds a Docker image from a Dockerfile located in the current working directory.

The container is started by the `TomodachiContainer` context manager.
When the context manager finishes, the built Docker image and containers are removed.

The `tomodachi_image` fixture uses `tomodachi_testcontainers.containers.EphemeralDockerImage`.
It automatically deletes the Docker image after the container is stopped.

Furthermore, the `tomodachi_container` fixture will start a new Tomodachi service container
and remove the old one for every test.

In this example, `tomodachi_container` fixture is used to test that the `GET /health` endpoint
returns status code `HTTP 200` and a correct JSON response.

```python
import httpx
import pytest

from tomodachi_testcontainers.containers import TomodachiContainer


@pytest.mark.asyncio()
async def test_healthcheck_passes(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

`tomodachi_container.get_external_url` returns the container's URL that is accessible from the
host, e.g. `http://localhost:12345`. The port is selected randomly by `get_available_port` function
that has been used in `tomodachi_container` fixture.

For inter-container communication, use `tomodachi_container.get_internal_url` instead.

That's it! 🎉 We have tested that the Docker image can be built and run, and that the service
is working as expected, all with a Docker container, on the highest test level - end-to-end.

### Change Dockerfile path, build context and build target

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

### Running Tomodachi container from pre-built image

If the Tomodachi service Docker image is already built, you can run the container
by specifying the image ID in the `TOMODACHI_TESTCONTAINER_IMAGE_ID` environment variable.

It is useful when running tests in the CI pipeline when the image has been already built
on the build step.
Instead of building a new image from scratch for the tests, we want to test the exact same image that
will be pushed to a Container Registry and deployed to production.

Examples:

- `TOMODACHI_TESTCONTAINER_IMAGE_ID=sha256:56ca9586de1cf25081bb5f070b59b86625b6221bb26d7409a74e6051d7954c92`
- `TOMODACHI_TESTCONTAINER_IMAGE_ID=mycompany/my-tomodachi-application:1.0.0`

⚠️ Make sure that the environment variable is set before running `pytest`.

### Testing Tomodachi service with external dependencies

The main benefit of Testcontainers is that it allows testing an application with
production-like external dependencies - databases, message brokers, file stores, HTTP APIs, etc.

For example, let's test a Tomodachi service that uses AWS S3 to store files.
The `TomodachiServiceS3` has one endpoint `GET /file/<key>` that returns a content of a file stored in AWS S3.

```python
import os

import tomodachi
from aiobotocore.session import get_session
from aiohttp import web
from types_aiobotocore_s3 import S3Client


def get_s3_client() -> S3Client:
    return get_session().create_client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
    )


class TomodachiServiceS3(tomodachi.Service):
    name = "service-s3"

    async def _start_service(self) -> None:
        self.bucket = "test-bucket"
        async with get_s3_client() as client:
            await client.create_bucket(Bucket=self.bucket)

    @tomodachi.http("GET", r"/file/(?P<key>[^/]+?)/?")
    async def get_file(self, request: web.Request, key: str) -> web.Response:
        async with get_s3_client() as client:
            s3_object = await client.get_object(Bucket=self.bucket, Key=key)
            content = await s3_object["Body"].read()
            return web.json_response({"content": content.decode()})
```

There are a couple of ways to test the service.

- Mock the AWS S3 client with `unittest.mock`:

  - The simplest way, but it doesn't test the actual AWS S3 integration.
  - We can't be sure that all calls to the AWS client are correct, without typos
    or surprising configuration mismatches.
  - Although unit tests are necessary, they won't give us the last bit of confidence that the service will work in production.
  - That's why it's necessary to _supplement_ unit tests with integration and end-to-end tests.

- Use a real AWS S3 bucket:

  - This is the most production-like way, but has some significant drawbacks in automated testing.
  - It requires a separate AWS account dedicated only to automated tests.
  - It's tricky to setup AWS credentials and permissions securely in the CI pipeline.
  - Need to be careful to not mutate production infrastructure.
  - Costs some money for using real AWS services.
  - It's slow, because we're making real network calls to AWS.

- Use cloud environment mock library like [LocalStack](https://localstack.cloud/) or [Moto](https://docs.getmoto.org/en/latest/)

  - Although it's not a real AWS, it's very close to simulating AWS services,
    so that it can be confidently used in cloud service integration tests.
  - Battle-tested and used by many organizations with wide community support.
  - Easy to use on a local machine and in the CI pipeline, simply run it in a Docker container and remove it when finished.
  - Works well with Testcontainers! This is the approach we'll take in this example. 🐳

As in the previous example, first, we need to create Tomodachi Testcontainer fixture
to build and run the service under test. It's done with a `tomodachi_container` fixture
in the example below.

```python
from typing import Generator, cast

import pytest
from docker.models.images import Image as DockerImage

from tomodachi_testcontainers.containers import LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def tomodachi_container(
    tomodachi_image: DockerImage,
    localstack_container: LocalStackContainer,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=str(tomodachi_image.id), edge_port=get_available_port())
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("tomodachi run app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)
    localstack_container.restart_container()
```

This time, `tomodachi_container` fixture is more involved. It uses
`localstack_container` fixture, provided by `tomodachi_testcontainers` library.
The fixture starts a `LocalStackContainer`.

After the `LocalStackContainer` is started, we can use its `get_internal_url` method
to get the URL of the container that is accessible _inside_ the Docker network.
This time, we need the internal URL of the container, because the `TomodachiContainer`
needs to communicate with `LocalStackContainer`, and they both run in the same Docker network.

The LocalStack's `internal_url` is passed to `TomodachiContainer` as an environment variable `AWS_S3_ENDPOINT_URL`,
following [12-factor app principle of providing app configuration in environment variables](https://12factor.net/config).

On `tomodachi_container` fixture teardown, `LocalStack` container is restarted
to reset its state - delete all S3 buckets and files. This way we can be sure
that each test starts with a clean state.
As alternative for calling `restart_container` method explicitly,
you can use `_restart_localstack_container_on_teardown` fixture.
We avoid flaky tests that depend on the state of the previous test or their execution order,
and avoid leaking test data from one test to another.
As a drawback, it takes a more time to restart a container after every test.
To improve test execution speed, you can explicitly cleanup AWS resources, for example,
deleting all S3 buckets and DynamoDB tables after every test.

That's the setup, now on to the application test. 🧪

```python
import httpx
import pytest
from types_aiobotocore_s3 import S3Client

from tomodachi_testcontainers.containers import TomodachiContainer


@pytest.mark.asyncio()
async def test_upload_and_read_file(
    tomodachi_container: TomodachiContainer,
    localstack_s3_client: S3Client,
) -> None:
    await localstack_s3_client.put_object(
        Bucket="test-bucket",
        Key="hello-world.txt",
        Body=b"Hello, World!",
    )

    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as http_client:
        response = await http_client.get("/file/hello-world.txt")

    assert response.status_code == 200
    assert response.json() == {"content": "Hello, World!"}
```

In the test setup/arrangement step, the test uses `localstack_s3_client`
fixture to upload a file to the AWS S3 bucket. The `localstack_s3_client`
is yet another helper fixture provided by `tomodachi_testcontainers`.
It creates a new S3 client configured to communicate with the `LocalStackContainer`.

For full list of available fixtures, check out
[tomodachi_testcontainers.pytest](src/tomodachi_testcontainers/pytest/) module.

In the act step, the test sends a request to the `GET /file/hello-world.txt` endpoint
to read the contents of a file, and in the assert step verifies that the response is correct.

⚠️ Note that to make the request to the running `TomodachiContainer`, the
`tomodachi_container.get_external_url` is used to get the URL
of the `TomodachiContainer` that is accessible from the host, because the
`pytest` runs on the host machine, and not inside the Docker network.

Awesome! 🚀 We have tested that our application is working with production-like
infrastructure, and established confidence that it will work
in the real environment as well.

For more examples, see [examples/](examples/) and tests in [tests/test_services](tests/test_services).

## Benefits and dangers of end-to-end tests

### Building confidence of releasability

The examples from this guide and [tests/test_services](tests/test_services) show that end-to-end tests
are powerful kind of tests. End-to-end test are used to test the system from its users perspective,
be it a human being or another application. End-to-end tests test the system from the outside,
on its public API level.

_End-to-end tests build the last bit of confidence of releasability -
that the system will work in production without more manual testing._

_To get a high confidence of releasability, it's necessary to test the system with real dependencies and infrastructure.
Testcontainers make it easy to spin up real dependencies in Docker containers, and throw them away
when the tests are finished. They work in thw same way locally and in the CI pipeline, so you need to
setup test suite only once._

### ⚠️ Mind the Test Pyramid - don't overdo end-to-end tests

Despite many benefits of end-to-end tests, they are the most expensive kind 💸 -
they're slow, sometimes [flaky](https://martinfowler.com/articles/nonDeterminism.html),
it's hard to understand what's broken when they fail.

End-to-end tests are expensive, but necessary to build confidence of releasability,
so it's important to use them intentionally and know about other kinds of tests.
After all, we can't be confident that the system _really_ works in production if we haven't
tested it in the environment as close to production as possible.

The [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) is a useful thinking model about
different kinds of tests and their value. It proposes that the majority of tests should be unit tests,
followed by integration tests, and the least amount of tests should be end-to-end tests.

The book [Architecture Patterns with Python](https://www.cosmicpython.com/) by Harry Percival and Bob Gregory
describes a useful [rule of thumb for use of different types of tests](https://www.cosmicpython.com/book/chapter_05_high_gear_low_gear.html#types_of_test_rules_of_thumb):

- **Aim for one end-to-end test per feature; error handling counts as a feature** - it suggests using
  end-to-end tests to demonstrate that the feature works, and all the system components that build
  the feature are working together correctly. _It means that end-to-end tests shouldn't be used
  as the main way of testing the system due to their cost and brittleness,
  but rather as a way to supplement service layer and unit tests._

- **Write the bulk of your tests against the service layer; maintain a small core of tests written against your domain model** -
  if you keep your application business logic use cases decoupled from the framework,
  you can test most of the system without the need to rely on slow, read dependencies.
  You can use fakes for simulating input/output (databases, message brokers, external system adapters),
  making the tests focused on the business logic.

The [Architecture Patterns with Python](https://www.cosmicpython.com/) book neatly describes patterns for building
robust and testable applications, so if you want to learn more, I highly recommend it as a starting point.
Also, it's free! 📖

Another point worth noting about different test types is that, ideally, tests should be written on the same level of abstraction. ⚖️

If means that if you're writing, for example, end-to-end tests, you should strive to use only the public API of the application -
HTTP endpoints, message topics or queues, etc. - to test the system, and not use any internal implementation details, like
directly accessing a database.

For example, the test `test_create_order` in [tests/test_services/test_order_service.py](tests/test_services/test_order_service.py)
asserts that an order has been created by calling the public API endpoints `GET /orders/<order_id>`,
instead of querying `orders` table directly to assert that the order row has been created with correct data.

This way, the internal `orders` table can be changed without breaking end-to-end tests,
as long as the public API stays the same. However, if the `GET /orders` has a bug,
all the tests that use `GET /orders` will fail, and it might not be intuitive to find the problem right away.
That's a trade-off we need to make in order to not expose system's private data structures and internal implementation details.

The same principle applies to other test types. In service layer tests, you'd be using only
use case functions to test the system, and not accessing domain model objects directly.
In case of domain model tests or unit tests, you'd be testing only public methods of the objects,
and not private methods and attributes.
Since there're no explicit private methods and attributes in Python, it's important to remember this,
and use automated code quality assertion tools like `flake8` and `pylint` as a safety net.

## Running Testcontainers in CI pipeline

To run Testcontainers in the CI pipeline, you'll need a container runtime installed
on the CI server (GitHub Actions, Jenkins etc.). That's pretty much it!

Running Testcontainers in the CI shouldn't be much different from running them locally.

For a complete example of how to run Testcontainers in the CI pipeline, check out
[tomodachi-testcontainers-github-actions](https://github.com/filipsnastins/tomodachi-testcontainers-github-actions)
repository.

## Supported Testcontainers

Phew! 😅
After going though all examples and understanding [benefits and dangers of end-to-end tests](#benefits-and-dangers-of-end-to-end-tests),
you're well-equipped to get the most value out of Testcontainers.

Bellow is the list of available Testcontainers in this library.
Feel free to explore how they're implemented and create your own Testcontainers as you go.
[testcontainers-python](https://github.com/testcontainers/testcontainers-python) provide and easy way
to create your own Testcontainers.

| Container Name | Default Image               | Fixture                |              Image Env Var Override |
| :------------- | :-------------------------- | :--------------------- | ----------------------------------: |
| Tomodachi      | n/a (build from Dockerfile) | `tomodachi_image`      |  `TOMODACHI_TESTCONTAINER_IMAGE_ID` |
| Moto           | `motoserver/moto:latest`    | `moto_container`       |       `MOTO_TESTCONTAINER_IMAGE_ID` |
| LocalStack     | `localstack/localstack:2.1` | `localstack_container` | `LOCALSTACK_TESTCONTAINER_IMAGE_ID` |
| SFTP           | `atmoz/sftp:latest`         | `sftp_container`       |       `SFTP_TESTCONTAINER_IMAGE_ID` |
| WireMock       | `wiremock/wiremock:latest`  | n/a                    |                                 n/a |

### Tomodachi

Tomodachi - a lightweight microservices library on Python asyncio.

Repository: <https://github.com/kalaspuff/tomodachi>

### Moto

Moto is a library that allows your tests to mock out AWS Services.

Repository: <https://github.com/getmoto/moto>

Docker Hub: <https://hub.docker.com/r/motoserver/moto>

### LocalStack

LocalStack provides an easy-to-use test/mocking framework for developing cloud applications.

Repository: <https://github.com/localstack/localstack>

DockerHub: <https://hub.docker.com/r/localstack/localstack>

### SFTP

Easy to use SFTP (SSH File Transfer Protocol) server with OpenSSH.

Repository: <https://github.com/atmoz/sftp>

DockerHub: <https://hub.docker.com/r/atmoz/sftp>

- Available as an extra dependency `sftp` - install with
  `pip install tomodachi-testcontainers[sftp]` or `poetry install -E sftp`

### WireMock

WireMock is a tool for building mock APIs. Create stable development environments,
isolate yourself from flakey 3rd parties and simulate APIs that don't exist yet.

Repository: <https://github.com/wiremock/wiremock>

DockerHub: <https://hub.docker.com/r/wiremock/wiremock>

## Configuration with environment variables

⚠️ Make sure that environment variables are set before running `pytest` -
e.g. with [pytest-env](https://pypi.org/project/pytest-env/) plugin or
by setting it in the shell before running `pytest`.

| Environment Variable                           | Description                                                                                                 |
| :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `TESTCONTAINER_DOCKER_NETWORK`                 | Launch testcontainers in specified Docker network. Defaults to 'bridge'. Network must be created beforehand |
| `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH`      | Override path to Dockerfile for building Tomodachi service image. (`--file` flag in `docker build` command) |
| `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT` | Override Docker build context                                                                               |
| `TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET`  | Override Docker build target (`--target` flag in `docker build` command)                                    |
| `<CONTAINER-NAME>_TESTCONTAINER_IMAGE_ID`      | Override any supported Testcontainer Image ID. Defaults to `None`                                           |
| `DOCKER_BUILDKIT`                              | Set `DOCKER_BUILDKIT=1` to use Docker BuildKit for building Docker images                                   |

## Change default Docker network

By default, testcontainers are started in the default `bridge` Docker network.
Sometimes it's useful to start containers in a different network, e.g. a network
specifically dedicated for running automated tests.

Specify a new network name with the `TOMODACHI_TESTCONTAINER_NETWORK` environment variable.
The Docker network is not created automatically, so make sure that it exists before running tests.

⚠️ Make sure that the environment variable is set before running `pytest`.

## Forward Testcontainer logs to Pytest

Logs from a testcontainer are forwarded to Python's standard logger as `INFO` logs when
`tomodachi_testcontainers.containers.DockerContainer` context manager exits.

To see the logs in Pytest, set the log level to at least `INFO` in [Pytest configuration](https://docs.pytest.org/en/7.1.x/how-to/logging.html).

Capturing container logs is useful to see what happened inside a container if a test failed.
It's especially useful if tests have failed in CI, because the containers are immediately deleted
after the test run, and there's nothing else to inspect apart from logs.

```toml
[tool.pytest.ini_options]
log_level = "INFO"
```

## Resources and acknowledgements

- [testcontainers.com](https://testcontainers.com/) - home of Testcontainers.

- [testcontainers-python](https://testcontainers-python.readthedocs.io/) - Python SDK for Testcontainers.

- Talk ["Integration tests are needed and simple"](https://softwaregarden.dev/en/talks/integration-tests-are-needed-and-simple/)
  by [Piotr Przybyl](https://softwaregarden.dev/en/) - explains the why behind the need
  for integration testing with read dependencies and gives a demo on Testcontainers.

- [tomodachi-testcontainers-github-actions](https://github.com/filipsnastins/tomodachi-testcontainers-github-actions) -
  example of running Testcontainers in the CI pipeline.

- [Awaitility](https://github.com/awaitility/awaitility) for Java and [busypie](https://github.com/rockem/busypie)
  for Python - libraries for testing asynchronous systems with async probes.

- <https://www.cosmicpython.com> - Architecture Patterns with Python book.
  Described [a rule of thumb for use of different types of tests in the test pyramid](https://www.cosmicpython.com/book/chapter_05_high_gear_low_gear.html#types_of_test_rules_of_thumb).

- <https://martinfowler.com/bliki/TestPyramid.html> - concise explanation of the test pyramid
  with useful references and further readings.

- Two contradictory articles about end-to-end tests:
  - <https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html>
  - <https://www.symphonious.net/2015/04/30/making-end-to-end-tests-work/>

## Development

- Install dev dependencies with [Poetry](https://python-poetry.org/)

```bash
poetry install --all-extras
poetry shell
pre-commit install
```

- Run tests

```bash
docker network create tomodachi-testcontainers

pytest
poetry run test-ci
```

- Format and lint code

```bash
poetry run format
poetry run lint
```

- Run all commit hooks at once

```bash
poetry run hooks
```

- Build package release

```bash
poetry build
```
