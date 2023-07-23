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
  - [Quickstart and Examples](#quickstart-and-examples)
  - [Getting started](#getting-started)
    - [Testing standalone Tomodachi service](#testing-standalone-tomodachi-service)
    - [Changing Dockerfile location](#changing-dockerfile-location)
    - [Running Tomodachi container from pre-built image](#running-tomodachi-container-from-pre-built-image)
    - [Testing Tomodachi service with external dependencies](#testing-tomodachi-service-with-external-dependencies)
  - [Benefits and dangers of end-to-end tests](#benefits-and-dangers-of-end-to-end-tests)
    - [Building confidence of releasability](#building-confidence-of-releasability)
    - [⚠️ Mind the Test Pyramid - not overdue end-to-end tests](#️-mind-the-test-pyramid---not-overdue-end-to-end-tests)
  - [Running Testcontainers in CI pipeline](#running-testcontainers-in-ci-pipeline)
  - [Supported Testcontainers](#supported-testcontainers)
    - [Tomodachi](#tomodachi)
    - [Moto](#moto)
    - [LocalStack](#localstack)
    - [SFTP](#sftp)
  - [Resources and acknowledgements](#resources-and-acknowledgements)
  - [Development](#development)

## Installation

```bash
pip install tomodachi-testcontainers

# Extra dependency - SFTP container and asyncssh
pip install tomodachi-testcontainers[sftp]
```

## Quickstart and Examples

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

 @tomodachi.http("GET", r"/health")
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

### Changing Dockerfile location

If the Dockerfile is not located in the current working directory, specify a new path
with the `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH` environment variable.

Examples:

- `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH=examples/` - specify just a directory, Dockerfile is inferred automatically
- `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH=examples/Dockerfile.testing` - explicitly specify the Dockerfile name

⚠️ Make sure that the environment variable is set before running `pytest` -
e.g. with [pytest-env](https://pypi.org/project/pytest-env/) plugin or
by setting it in the shell before running `pytest`.

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
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.environ.get("AWS_S3_ENDPOINT_URL"),
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
    _restart_localstack_container: None,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=str(tomodachi_image.id), edge_port=get_available_port())
        .with_env("AWS_REGION", "eu-west-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("tomodachi run app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)
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

The `tomodachi_container` fixture also uses the `_restart_localstack_container` fixture,
that restarts the `LocalStackContainer` after every test.
It resets the state of LocalStack after every test so that each new test starts
from a clean and predictable state. That way, we avoid flaky tests that depend on the
state of the previous test or their execution order.
As a downside, it takes a bit more time to restart the container after every test,
so it might not be necessary for every test.

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

### ⚠️ Mind the Test Pyramid - not overdue end-to-end tests

Despite many benefits of end-to-end tests, they are the most expensive kind 💸 -
they're slow, sometimes [flaky](https://martinfowler.com/articles/nonDeterminism.html),
it's hard to understand what's broken when they fail.

End-to-end tests are expensive, but necessary to build confidence of releasability,
so it's important to use them intentionally and know about other kinds of tests.
After all, we can't be confident that the system _really_ works in production if we haven't
tested it in the environment as close as possible as production.

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

Bellow is the list of available Testcontainers in this library, but feel free to explore how they're
implemented and create your own Testcontainers as you go.
[testcontainers-python](https://github.com/testcontainers/testcontainers-python) provide and easy way
to create your own Testcontainers.

| Container Name | Default Image               | Fixture                |                                                        Image Env Var Override |
| :------------- | :-------------------------- | :--------------------- | ----------------------------------------------------------------------------: |
| Tomodachi      | n/a (build from Dockerfile) | `tomodachi_image`      | `TOMODACHI_TESTCONTAINER_IMAGE_ID`, `TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH` |
| Moto           | `motoserver/moto:latest`    | `moto_container`       |                                                 `MOTO_TESTCONTAINER_IMAGE_ID` |
| LocalStack     | `localstack/localstack:2.1` | `localstack_container` |                                           `LOCALSTACK_TESTCONTAINER_IMAGE_ID` |
| SFTP           | `atmoz/sftp:latest`         | `sftp_container`       |                                                 `SFTP_TESTCONTAINER_IMAGE_ID` |

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
