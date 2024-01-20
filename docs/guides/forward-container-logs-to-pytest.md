# Forward Container Logs to pytest

Logs from a container are forwarded to Python's standard logger as `INFO` logs when
[`DockerContainer`][tomodachi_testcontainers.DockerContainer] context manager exits.

To see the logs in pytest, set the log level to at least `INFO` in the [pytest configuration](https://docs.pytest.org/en/7.1.x/how-to/logging.html).

```toml
[tool.pytest.ini_options]
log_level = "INFO"
```

!!! success

    Capturing container logs is useful to see what has happened inside a container when a test has failed.
    It's especially useful if tests have failed in the deployment pipeline,
    because the containers are immediately deleted after the test run, and there's nothing else to inspect apart from the logs.

By default, pytest won't show any output if all tests pass.
To see the logs in the console, run `pytest` with `-rA` flag, e.g., `pytest -rA`.
It will show A(ll) test summary, including captured logs.

```sh
-r chars   Show extra test summary info as specified by chars:
    (f)ailed, (E)rror, (s)kipped, (x)failed, (X)passed,
    (p)assed, (P)assed with output, (a)ll except passed (p/P), or (A)ll.
    (w)arnings are enabled by default (see --disable-warnings),
    'N' can be used to reset the list. (default: 'fE').
```

Example log output:

```sh
pytest tests/services/test_service_healthcheck.py -rA
```

<figure markdown>
  ![Testcontainers logs - test passed](../images/pytest-with-testcontainers-logs-passed-test.png)
</figure>

```sh
pytest tests/services/test_service_s3.py -k test_upload_and_read_file
```

<figure markdown>
  ![Testcontainer logs - test failed](../images/pytest-with-testcontainers-logs-failed-test.png)
</figure>
