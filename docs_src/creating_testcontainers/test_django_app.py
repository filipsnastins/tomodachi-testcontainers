from typing import Generator

import pytest
import requests

from tomodachi_testcontainers import DockerContainer, WebContainer


class DjangoContainer(WebContainer):
    def __init__(self, image: str) -> None:
        super().__init__(
            image=image,
            internal_port=8000,
            http_healthcheck_path="/health",
        )

    def log_message_on_container_start(self) -> str:
        return f"Django web app: http://localhost:{self.edge_port}"


@pytest.fixture(scope="session")
def django_container(testcontainer_image: str) -> Generator[DockerContainer, None, None]:
    with (
        DjangoContainer(testcontainer_image)
        .with_env("GREET", "Testcontainers")
        .with_command("python creating_testcontainers/django_app/manage.py runserver 0.0.0.0:8000")
    ) as container:
        yield container


def test_greetings_from_django(django_container: DjangoContainer) -> None:
    base_url = django_container.get_external_url()

    response = requests.get(f"{base_url}/hello", timeout=10)

    assert response.json() == {"message": "Hello from Django, Testcontainers!"}
