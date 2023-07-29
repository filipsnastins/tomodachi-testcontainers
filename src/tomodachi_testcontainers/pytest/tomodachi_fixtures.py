import os
from pathlib import Path
from typing import Generator

import pytest
from docker.models.images import Image as DockerImage

from tomodachi_testcontainers.containers import EphemeralDockerImage, get_docker_image


@pytest.fixture(scope="session")
def tomodachi_image() -> Generator[DockerImage, None, None]:
    if image_id := os.environ.get("TOMODACHI_TESTCONTAINER_IMAGE_ID"):
        yield get_docker_image(image_id)
    else:
        dockerfile = Path(os.environ.get("TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH", "."))
        with EphemeralDockerImage(dockerfile) as image:
            yield image
