# Exporting Test Coverage

TODO

Since Testcontainers run in a separate Docker container, their code coverage will not be included to the coverage report by default.

Assuming you're using [coverage.py](https://github.com/nedbat/coveragepy) or [pytest-cov](https://github.com/pytest-dev/pytest-cov),
to see the code coverage from the Testcontainer, you need to export the `.coverage` file from the container to the host machine,
and then append it to the root `.coverage` report.

To generate the code coverage report from `TomodachiContainer`, start the container with the `coverage run -m tomodachi run ...` command.
The `coverage` tool will keep track of the code that has been executed in the container,
and write the coverage report to `.coverage` file when the container stops.

```py
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def tomodachi_container(testcontainers_docker_image: str) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=testcontainers_docker_image,
        edge_port=get_available_port(),
    ).with_command(
        "bash -c 'pip install coverage[toml] && coverage run -m tomodachi run src/healthcheck.py --production'"
    ) as container:
        yield cast(TomodachiContainer, container)
```

Configure the `coverage` tool in the `pyproject.toml` file - see [examples/pyproject.toml](examples/pyproject.toml).

To signal the `TomodachiContainer` to export the `.coverage` file when the container stops,
set the `TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE` environment variable to `1`.
Coverage export is disabled by default to not pollute the host machine with `.coverage` files.
Generally, you'll be running tests with coverage in the deployment pipeline,
so set the environment variable in the CI/CD server configuration.

Tying it all together, run pytest with the coverage mode:

```sh
TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1 pytest --cov --cov-branch
```

The `.coverage` file will be saved on the host machine in the current working directory.
Also, see [dev.py::test_ci](dev.py) for an example of how this project is running tests with code coverage in the deployment pipeline.

If source code paths are different in the container and on the host machine, e.g. because the container
is running in a different directory, you might have to re-map the paths with `coverage` tool.
See [Re-mapping paths](https://coverage.readthedocs.io/en/7.3.2/cmd.html#re-mapping-paths) in the
`coverage.py` documentation, and configuration example in the [pyproject.toml](pyproject.toml) (search for 'tool.coverage' section).

See an example of how the combined test coverage looks at <https://app.codecov.io/gh/filipsnastins/tomodachi-testcontainers>.
The [examples/](examples/) services are tested only with Testcontainer tests, and their coverage is included in the final report.
