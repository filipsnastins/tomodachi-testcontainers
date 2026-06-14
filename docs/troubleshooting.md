# Troubleshooting

This section describes common errors you might encounter working with Testcontainers in the Python environment.

---

Error on running tests with pytest: `ScopeMismatch: You tried to access the function scoped fixture event_loop with a session scoped request object, involved factories.`

: **Problem:** the error occurs when you're using asynchronous fixtures with a scope higher than `function`,
e.g., fixture `moto_container` has `session` scope.
The default `event_loop` fixture provided by `pytest-asyncio` is a function-scoped fixture, so it can't be used with session-scoped fixtures.

: **Solution:** override the `event_loop` fixture with a session-scoped fixture by placing it in your project's default `conftest.py`.

    ```py title="tests/conftest.py"
    --8<--
    docs_src/conftest.py
    --8<--
    ```

---

Error when using a Docker Desktop alternative (Colima, Rancher Desktop, Podman, OrbStack):
`docker.errors.DockerException: Error while fetching server API version`
or `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`.

: **Problem:** Testcontainers connects to Docker through `docker.from_env()`, which reads the
`DOCKER_HOST` environment variable but **does not** read the Docker CLI context (`docker context use ...`).
Docker Desktop alternatives usually place their socket somewhere other than `/var/run/docker.sock`,
so even though the `docker` CLI works, Testcontainers tries the default socket and fails to connect.

: **Solution:** point `DOCKER_HOST` at the active runtime's socket. The most portable way is to derive
it from the active Docker context:

    ```sh
    export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
    ```

    Or set it explicitly for your runtime, for example:

    ```sh
    # Colima
    export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
    # Rancher Desktop
    export DOCKER_HOST="unix://$HOME/.rd/docker.sock"
    # OrbStack
    export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"
    ```

    Add the export to your shell profile (or set it via [pytest-env](https://pypi.org/project/pytest-env/))
    so it is present whenever you run `pytest`.

---
