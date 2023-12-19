# Parallelizing Tests

Running tests in parallel reduces deployment pipeline runtime and shortens the feedback loop developers get from the tests.

Tests that use Testcontainers are fast even when run sequentially; however, in certain circumstances, they can be slow:

- Tests are not isolated, and containers are restarted or recreated after every test to prevent state leaks.
- Tests rely on slow dependencies.
- The application under test performs compute-intensive tasks.
- The application under test is slow due to a bug.

If the tests are slow due to a bug in the application code, consider fixing the root cause;
parallelizing tests will hide the problem from the tests and let it slip into production.
If the tests are slow due to the problematic test design or inherently slow dependencies,
parallelizing tests will improve the runtime. However, if time allows, consider improving the test design,
for example, by starting all containers once per test run and managing data isolation with the application means.

!!! success "Try it out!"

    Experiment with running tests in parallel - it will save you time if the tests are run frequently (as they should be).

## Parallelizing tests with pytest-xdist

The [pytest-xdist](https://pytest-xdist.readthedocs.io/en/latest/index.html) plugin allows running tests in parallel across multiple CPUs.
To get started, install the plugin with `pip install pytest-xdist`,
and run [pytest](https://docs.pytest.org/en/latest/) in parallel mode:

```sh
pytest -n auto
```

With the `-n auto` flag, the tests are distributed across all available CPU cores.
Refer to the [pytest-xdist](https://pytest-xdist.readthedocs.io/en/latest/index.html) documentation for detailed usage options.

`pytest-xdist` runs tests across multiple separate worker processes.
A worker is assigned a subset of tests, and each worker will create its own set of Testcontainers,
i.e., run all `pytest` fixtures independently, even the session-scoped fixtures.
It will increase the number of running containers by the number of test workers and ultimately use more resources.

!!! note

    Running tests in parallel requires more compute resources. Generally, it's not a problem,
    but be mindful of the associated costs and resource usage limits, especially with cloud CI/CD platforms.

Since test workers are isolated, there shouldn't be any problems with test data leaks between the workers,
unless they're competing for the same global resources, e.g., writing to files with the same name.
To fix such problems, separate the resources with unique identifiers:
[temporary path and file fixtures](https://docs.pytest.org/en/latest/how-to/tmp_path.html) (`tmp_path` and similar fixtures from `pytest`)
and [unique test run prefixes](https://docs.pytest.org/en/latest/how-to/tmp_path.html)
(`testrun_uid` fixture from `pytest-xdist`).
