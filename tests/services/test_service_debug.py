"""An example of attaching a debugger to a running Tomodachi testcontainer.

Generally you won't need a debugger in the testcontainer often,
because you should be able to detect most issues by checking the logs,
in the same way as you would to when investigating an issue in a production environment.
"""

from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="module")
def service_healthcheck_container(testcontainers_docker_image: str) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=testcontainers_docker_image, edge_port=get_available_port())
        # Bind debugger port.
        .with_bind_ports(5678, 5678)
        # Explicitly install debugpy. Adding the debugpy to dev dependencies in pyproject will not work
        # because the image is using the 'release' target which doesn't include dev dependencies.
        # Adding the debugpy to production dependencies is not recommended.
        .with_command(
            'bash -c "pip install debugpy; python -m debugpy --listen 0.0.0.0:5678 -m tomodachi run src/healthcheck.py --production"'  # pylint: disable=line-too-long
        )
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="module")
async def http_client(service_healthcheck_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_healthcheck_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_healthcheck_passes(http_client: httpx.AsyncClient) -> None:
    # To start the debugging, place a breakpoint in the test and in the production code.
    # If using VSCode, run the test in the debugger and then attach the remote debugger on container port 5678.

    # https://code.visualstudio.com/docs/python/debugging#_debugging-by-attaching-over-a-network-connection
    # See .vscode/launch.example.json.

    # Timeout set to None to avoid getting a TimeoutError while working in the debugger.
    response = await http_client.get("/health", timeout=None)

    # Set a breakpoint after sending the HTTP request to the container, e.g. on the next line.
    # It will trigger the breakpoint set in the production code and won't stop the running containers while debugging.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
