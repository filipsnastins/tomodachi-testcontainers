# Old

TODO delete

Systems don't live in isolation. They depend on other systems - other internal applications, databases,
file exchange services, cloud provider services, third-party services outside our control, etc.

The main benefit of Testcontainers is that it allows testing an application with
production-like external dependencies - databases, message brokers, file stores, HTTP APIs, etc.

For example, let's test a Tomodachi service that uses AWS S3 to store files.
The `Service` has one endpoint `GET /file/<key>` that returns a content of a file stored in AWS S3.

```py
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


class Service(tomodachi.Service):
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
  - It's tricky to setup AWS credentials and permissions securely in the deployment pipeline.
  - Need to be careful to not mutate production infrastructure.
  - Costs some money for using real AWS services.
  - It's slow, because we're making real network calls to AWS.

- Use cloud environment mock library like [LocalStack](https://localstack.cloud/) or [Moto](https://docs.getmoto.org/en/latest/)

  - Although it's not a real AWS, it's very close to simulating AWS services,
    so that it can be confidently used in cloud service integration tests.
  - Battle-tested and used by many organizations with wide community support.
  - Easy to use on a local machine and in the deployment pipeline, simply run it in a Docker container and remove it when finished.
  - Works well with Testcontainers! This is the approach we'll take in this example. 🐳

As in the previous example, first, we need to create Tomodachi Testcontainer fixture
to build and run the service under test. It's done with a `tomodachi_container` fixture
in the example below.

```py
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def tomodachi_container(
    testcontainers_docker_image: str,
    localstack_container: LocalStackContainer,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=testcontainers_docker_image, edge_port=get_available_port())
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("tomodachi run app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)
    localstack_container.restart()
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
As alternative for calling `restart` method explicitly,
you can use `restart_localstack_container_on_teardown` fixture.
We avoid flaky tests that depend on the state of the previous test or their execution order,
and avoid leaking test data from one test to another.
As a drawback, it takes a more time to restart a container after every test.
To improve test execution speed, you can explicitly cleanup AWS resources, for example,
deleting all S3 buckets and DynamoDB tables after every test.

That's the setup, now on to the application test. 🧪

```py
import httpx
import pytest
from types_aiobotocore_s3 import S3Client

from tomodachi_testcontainers import TomodachiContainer


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
when the tests are finished. They work in the same way locally and in the deployment pipeline, so you need to
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
  you can test most of the system without the need to rely on slow, real dependencies.
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
