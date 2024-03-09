from typing import Generator

import pytest
import requests

from tomodachi_testcontainers import DockerContainer, WebContainer


class FlaskContainer(WebContainer):
    def __init__(self, image: str) -> None:
        super().__init__(
            image=image,
            internal_port=5000,
            http_healthcheck_path="/health",
        )

    def log_message_on_container_start(self) -> str:
        return f"Flask web app: http://localhost:{self.edge_port}"


@pytest.fixture(scope="session")
def flask_container(testcontainer_image: str) -> Generator[DockerContainer, None, None]:
    with (
        FlaskContainer(testcontainer_image)
        .with_env("GREET", "Testcontainers")
        .with_command("flask --app creating_testcontainers/flask_app.py run --host 0.0.0.0 --port 5000")
    ) as container:
        yield container


def test_greetings_from_flask(flask_container: FlaskContainer) -> None:
    base_url = flask_container.get_external_url()

    response = requests.get(f"{base_url}/hello", timeout=10)

    assert response.json() == {"message": "Hello from Flask, Testcontainers!"}
