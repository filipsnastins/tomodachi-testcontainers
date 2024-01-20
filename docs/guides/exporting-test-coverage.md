# Exporting Test Coverage

When testing applications that run in Docker containers, their [code coverage](https://en.wikipedia.org/wiki/Code_coverage)
will not be included in the report by default.

Assuming you're using [coverage.py](https://github.com/nedbat/coveragepy) or [pytest-cov](https://github.com/pytest-dev/pytest-cov),
to get the code coverage from the Testcontainer, you need to export the `.coverage` file from the container to the host machine
and append it to the root `.coverage` report.

To generate the code coverage report from [`TomodachiContainer`][tomodachi_testcontainers.TomodachiContainer],
start the container with the `coverage run -m tomodachi run ...` command.
The `coverage` tool will keep track of the code that has been executed,
and write the coverage report to `.coverage` file when the container stops.

```py hl_lines="14"
--8<--
tests/services/test_service_healthcheck.py:tomodachi_container
--8<--
```

Configure the `coverage` tool in the `pyproject.toml` file:

```toml
[tool.poetry.group.test]
optional = true

[tool.poetry.group.test.dependencies]
pytest-cov = "^4.1.0"

[tool.coverage.run]
branch = true
source = ["src/"]
```

To signal the `TomodachiContainer` to export the `.coverage` file when the container stops,
set the `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE` environment variable to `1`.
Coverage export is disabled by default not to pollute the host machine with `.coverage` files.
Generally, you'll be running tests with coverage in the deployment pipeline, so set the environment variable in the CI/CD server configuration.

Tying it all together, run `pytest` with the coverage mode. The `.coverage` file will be saved in the current working directory on the host machine.

```sh
TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1 pytest --cov --cov-branch
```

Here's an example of how this project runs tests with code coverage in the deployment pipeline
([dev.py](https://github.com/filipsnastins/tomodachi-testcontainers/blob/main/dev.py)).

```sh
coverage erase

TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1 pytest \
    --cov
    --cov-append \
    --cov-branch \
    --cov-report=xml:build/coverage.xml \
    --cov-report=html:build/htmlcov \
    -v \
    --junitxml=build/tests.xml
```

If source code paths are different in the container and on the host machine, e.g., because the container
is running in a different directory, you might have to re-map the paths with `coverage` tool.
See [Re-mapping paths](https://coverage.readthedocs.io/en/7.3.2/cmd.html#re-mapping-paths) in the `coverage.py` documentation.

See an example of how the combined test coverage looks at <https://app.codecov.io/gh/filipsnastins/tomodachi-testcontainers>.
The [examples/](https://github.com/filipsnastins/tomodachi-testcontainers/tree/main/examples)
services are tested only with Testcontainer tests; their coverage is included in the final report.
