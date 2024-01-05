## Forward Testcontainer Logs to pytest

Logs from a testcontainer are forwarded to Python's standard logger as `INFO` logs when
`tomodachi_testcontainers.DockerContainer` context manager exits.

To see the logs in pytest, set the log level to at least `INFO` in [pytest configuration](https://docs.pytest.org/en/7.1.x/how-to/logging.html).

Capturing container logs is useful to see what happened inside a container if a test failed.
It's especially useful if tests have failed in CI, because the containers are immediately deleted
after the test run, and there's nothing else to inspect apart from logs.

```toml
[tool.pytest.ini_options]
log_level = "INFO"
```

By default, `pytest` won't show any output if all tests pass. To see the logs in the console, run `pytest` with `-rA` flag,
e.g. `pytest -rA`. It will show extra summary for A(ll) tests, including captured logs.

```sh
-r chars              Show extra test summary info as specified by chars: (f)ailed, (E)rror, (s)kipped, (x)failed, (X)passed, (p)assed, (P)assed with output, (a)ll except passed (p/P), or (A)ll. (w)arnings are enabled by default (see --disable-warnings), 'N' can be used to reset the list. (default: 'fE').
```

- `pytest tests/services/test_service_healthcheck.py -rA`

![Testcontainers logs - test passed](docs/images/pytest-with-testcontainers-logs-passed-test.png)

- `pytest tests/services/test_service_s3.py -k test_upload_and_read_file`

![Testcontainer logs - test failed](docs/images/pytest-with-testcontainers-logs-failed-test.png)
