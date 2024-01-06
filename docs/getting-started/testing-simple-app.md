# Testing Simple Application

## Creating a simple web application

Let's start with a simple `hello, world` web application.
The app has one endpoint, `GET /hello`, that greets you with the name given in the query parameter.

```py title="src/hello.py"
--8<-- "docs_src/getting_started/hello.py"
```

We want to test that the application behaves as expected and all its components are configured correctly -
framework, Docker container, and dependencies. We can achieve that with an _end-to-end (E2E)_ test
that starts the application as a Docker container, sends an HTTP request, and asserts that the response is correct.

## Creating a first Testcontainer

Before writing the test, we need to start the application in a Docker container.

```py title="tests/test_hello.py" hl_lines="9 12-13"
--8<--
docs_src/getting_started/test_hello001.py:tomodachi_container
--8<--
```

The [`testcontainers_docker_image`][tomodachi_testcontainers.pytest.testcontainers_docker_image] fixture builds the Docker image with
a [Dockerfile](https://github.com/filipsnastins/tomodachi-testcontainers/blob/main/examples/Dockerfile) from the current working directory,
and removes the Docker image when all tests finish.

The [`TomodachiContainer`][tomodachi_testcontainers.TomodachiContainer] receives the built image ID and a randomly available port as input arguments
and starts the Testcontainer in a context manager. The context manager deletes the Testcontainer on exit.

The `tomodachi_container` fixture is assigned the `session` scope to create the container only once per test session.
It's a good practice to create Testcontainers only once for better test performance - it takes some time for a Docker container to start,
and the test suite will become slow if containers are recreated for every test.

## Writing an end-to-end test

Having the `tomodachi_container` fixture, we can write our first end-to-end test.
Let's test that the application greets us with `Hello, Testcontainers!` when we provide it the `?name=Testcontainers` parameter.

```py title="tests/test_hello.py"
--8<--
docs_src/getting_started/test_hello001.py:test_hello_testcontainers
--8<--
```

The test configures the [httpx](https://www.python-httpx.org/) HTTP client with the Testcontainer's base URL.
The `tomodachi_container.get_external_url()` returns a URL for accessing the Docker container from the host machine;
in a format like `http://localhost:1234` (the port is assigned randomly).
Finally, we send the `GET /hello?name=Testcontainers` request and assert that we received the expected response.
That's it! We ensured that our application started, all its components were configured correctly and worked as expected.

Let's test the default case when the `name` query parameter is not provided.

```py title="tests/test_hello.py"
--8<--
docs_src/getting_started/test_hello001.py:test_hello_world
--8<--
```

!!! note "End-to-end or integration test?"

    What's the difference between end-to-end and integration tests?
    It depends on the context *where* the tests are written and *what* they are testing.
    Often, the term end-to-end test is used when talking about tests that test the behavior of *multiple applications*
    working together to achieve some valuable outcome. Usually, such tests are developed in a separate code repository
    and run in a staging environment, not on the developer's local computer.
    The term integration test can refer to tests that exercise a subset of the whole system, e.g., two applications
    working together. Also, it can be used when referring to testing that a single application's internal components are working together correctly.

    In the context of Testcontainers, we're creating **isolated tests for a single application that runs in a controlled environment**.
    An application consists of multiple sub-components: framework, runtime environment like OS in a Docker container, programming language
    dependencies, third-party packages, etc. Testing that all components are configured correctly and working together gives
    you immediate feedback and eases future maintenance - having such tests helps upgrade dependencies effortlessly,
    which is necessary for keeping your system secure. Also, we want to test the application's behavior to ensure it delivers the desired outcome.
    So, apart from testing that the application works, we'll verify that it does the right thing.

    Therefore, when testing a single application in isolation, the terms end-to-end and integration tests are fuzzy and often describe the same thing.
    I'll stick with the end-to-end tests because they better describe the tests we're writing in these guides -
    the tests that exercise the application's public API end-to-end, sending requests and asserting the responses.

    There are no ultimately correct terms - select the one that makes the most sense in your context and problem domain,
    and stick with it; it might be something entirely different.

## Creating test fixtures

You might have noticed a duplication in how we configure the `httpx.AsyncClient` in every test.
It calls for a new fixture. Let's create the `http_client` fixture and refactor the tests.

```py title="tests/test_hello.py" hl_lines="8 14 22"
--8<--
docs_src/getting_started/test_hello002.py:tests
--8<--
```

Now, the code is a little bit cleaner. A problem with end-to-end tests is that the code can get lengthy as we create more complex test cases.
It's due to the accidental complexity of the high-level protocols we're working with, e.g., calling HTTP endpoints requires setup and boilerplate code.
To keep the tests clean, notice such duplications and complexities and refactor the code with fixtures and helper functions.
