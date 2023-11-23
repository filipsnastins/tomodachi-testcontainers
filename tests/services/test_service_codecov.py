import tarfile
from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio
from docker.models.containers import Container
from docker.models.images import Image

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port

PROJECT_ROOT = Path(__file__).parent.parent.parent


class GracefulTomodachiContainer(TomodachiContainer):
    def copy(self, path) -> None:
        stream, _ = self.get_wrapped_container().get_archive(path)
        with tarfile.open(fileobj=BytesIO(b"".join(stream))) as f:
            f.extractall(path=PROJECT_ROOT)

    def stop(self) -> None:
        container = self._container or cast(Container, self.get_docker_client().client.containers.get(self._name))
        container.stop()
        self.copy("/app/.coverage.testcontainer")
        super().stop()


@pytest.fixture(scope="module")
def service_healthcheck_container(testcontainers_docker_image: Image) -> Generator[TomodachiContainer, None, None]:
    with GracefulTomodachiContainer(
        image=str(testcontainers_docker_image.id),
        edge_port=get_available_port(),
    ).with_command(
        "bash -c 'pip install pytest-cov && coverage run --source src --data-file .coverage.testcontainer -m tomodachi run src/healthcheck.py --production'"
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="module")
async def http_client(service_healthcheck_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_healthcheck_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_healthcheck_passes(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
