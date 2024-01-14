from typing import Generator, cast

import pytest
import requests

from tomodachi_testcontainers.containers.common import WebContainer
from tomodachi_testcontainers.utils import get_available_port


class FastAPIContainer(WebContainer):
    def __init__(self, image: str) -> None:
        super().__init__(
            image=image,
            internal_port=8000,
            edge_port=get_available_port(),
            http_healthcheck_path="/health",
        )

    def log_message_on_container_start(self) -> str:
        return f"FastAPI web app: http://localhost:{self.edge_port}"


@pytest.fixture(scope="session")
def fastapi_container(testcontainers_docker_image: str) -> Generator[FastAPIContainer, None, None]:
    with (
        FastAPIContainer(image=testcontainers_docker_image)
        .with_env("GREET", "Testcontainers")
        .with_command("uvicorn creating_testcontainers.fastapi_app:app --host 0.0.0.0 --port 8000")
    ) as container:
        yield cast(FastAPIContainer, container)


def test_greetings_from_fastapi(fastapi_container: FastAPIContainer) -> None:
    base_url = fastapi_container.get_external_url()

    response = requests.get(f"{base_url}/hello", timeout=10)

    assert response.json() == {"message": "Hello from FastAPI, Testcontainers!"}
