# Debugging Testcontainers

Debugging failing Testcontainer tests can be tricky.
The code is running in separate ephemeral Docker containers that are immediately deleted after the test run finishes.

Below are some debugging and exploratory testing tips to help you debug failing Testcontainer tests.

## 1. Inspect container logs

Logs are the main source of information when debugging Testcontainers.
Generally, you should be able to pinpoint any problem by looking at the container logs
in the same way as you'd investigate a problem in a production environment.
If you find it difficult to understand how the system behaves from the logs, it's a sign that the logging is insufficient and needs improvement.

By default, `tomodachi_testcontainers` will forward all container logs to Python's standard logger as `INFO` logs when containers stop.
See [Forward Container Logs to pytest](./forward-container-logs-to-pytest.md)
section for more information and examples of configuring pytest to show the logs.

Running Testcontainer tests is a great way to do exploratory testing of the system,
check out if log messages are meaningful, and it's easy to understand what the system is doing.

## 2. Pause a test with a breakpoint and inspect running containers

Testcontainers are ephemeral - they're removed immediately after the test run finishes.
Sometimes, it's helpful to inspect the state of running containers, e.g.,
manually check the contents of a database, S3 buckets, message queues, or application logs.

To do that, pause the execution of a test with a breakpoint and manually inspect running containers:

```py
import httpx
import pytest


@pytest.mark.asyncio()
async def test_healthcheck_passes(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/health")

    # The breakpoint will pause the execution of the test
    # and allow you to inspect running Docker containers.
    breakpoint()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

## 3. Use helper containers and tools for exploratory testing

When logs are insufficient to understand what's going on, it's helpful to use other helper containers and tools
for inspecting container state, e.g., what's in the database, S3 buckets, message queues, etc.

[Pause a test with a breakpoint](#2-pause-a-test-with-a-breakpoint-and-inspect-running-containers)
and inspect running containers with other tools, for example:

- Use AWS CLI with `aws --endpoint-url=http://localhost:<port>` to inspect the state of `LocalStack` or `Moto` containers.
  Find out `LocalStack` or `Moto` port in the debug console output or inspect the containers with `docker ps`.
- `Moto` provides a convenient [web UI dashboard](https://docs.getmoto.org/en/latest/docs/server_mode.html#dashboard).
  Find the link to the Moto dashboard in the pytest console output.
- Use the [`DynamoDBAdminContainer`][tomodachi_testcontainers.DynamoDBAdminContainer] to inspect the state of DynamoDB tables.

## 4. Attach a remote debugger to a running container

As a last resort, you can attach a remote debugger to an application running in a remote container,
e.g., to a [`TomodachiContainer`][tomodachi_testcontainers.TomodachiContainer] running your application code.

If using `VScode`, see the [VSCode documentation](https://code.visualstudio.com/docs/python/debugging#_debugging-by-attaching-over-a-network-connection)
of attaching a remote debugger to a running process over HTTP.

```py
--8<-- "tests/services/test_service_debug.py"
```

## 5. Inspect Testcontainers with Testcontainers Desktop App

[Testcontainers Desktop](https://testcontainers.com/desktop/) app allows you to prevent container shutdown
so you can inspect and debug them, and it has some other extra features.
