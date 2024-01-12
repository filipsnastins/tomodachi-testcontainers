# Features

## Containers

See the list of available Testcontainers at [`tomodachi_testcontainers`][tomodachi_testcontainers].
Find more Testcontainers in the official [testcontainers-python](https://github.com/testcontainers/testcontainers-python) library.
See [Creating New Testcontainers](./guides/creating-new-testcontainers.md) for adding new Testcontainers.

## Pytest fixtures and helpers

**Ready-made pytest fixtures** make testing your applications simple.
Find the complete list of available fixtures at [`tomodachi_testcontainers.pytest.fixtures`][tomodachi_testcontainers.pytest.fixtures].

- [`testcontainers_docker_image`][tomodachi_testcontainers.pytest.testcontainers_docker_image]
  fixture automatically builds a Docker image with a Dockerfile from the current working directory.
  It allows you to run the latest version of our application as a Docker container for automated testing.

- Launch commonly used Testcontainers with fixtures, e.g.,
  [`localstack_container`][tomodachi_testcontainers.pytest.localstack_container],
  [`postgres_container`][tomodachi_testcontainers.pytest.postgres_container],
  etc.

- Get fixtures for interacting with Testcontainers, e.g., `localstack_s3_client`, `moto_dynamodb_client`, etc.

**Async probes** for [testing asynchronous systems](./getting-started/testing-asynchronous-systems) -
[`tomodachi_testcontainers.pytest.async_probes`][tomodachi_testcontainers.pytest.async_probes].
Inspired by [Awaitility](http://www.awaitility.org/) and [busypie](https://github.com/rockem/busypie).

**Assertion helpers** for common test cases like asserting for logs in a Docker container -
[`tomodachi_testcontainers.pytest.assertions`][tomodachi_testcontainers.pytest.assertions].

**Utility functions** in [`tomodachi_testcontainers.utils`][tomodachi_testcontainers.utils] for easier working with Testcontainers.

## Test clients

**Test clients** allow you to test different modes of interactions with your applications.

- [`SNSSQSTestClient`][tomodachi_testcontainers.clients.SNSSQSTestClient] helps test
  [Tomodachi](https://github.com/kalaspuff/tomodachi) applications that communicate through AWS SNS SQS.

## Logging

Upon Testcontainers' shutdown, their logs are forwarded to Python's logger, making it possible to see what happened inside the containers.
It's useful for debugging failing tests, especially in a deployment pipeline,
because containers are immediately deleted when the test run finishes, leaving behind only their logs.

## Configuration

Most features are configurable with environment variables, e.g., a path to Dockerfile, Testcontainer image versions, etc.
See all [configuration options](./configuration-options.md).
