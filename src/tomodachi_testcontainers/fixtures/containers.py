import os
from pathlib import Path
from typing import Generator

import pytest

from .. import EphemeralDockerImage


@pytest.fixture(scope="session")
def testcontainer_image() -> Generator[str, None, None]:
    """Builds a Docker image from a Dockerfile located in the current working directory and returns an image ID.

    The Docker image is removed on test session end.

    Configuration environment variables (set on host machine):

    - `TESTCONTAINER_IMAGE_ID` - use given Image ID for creating a container.
    - `TESTCONTAINER_DOCKERFILE_PATH` - override path to the Dockerfile for building Docker image.
    - `TESTCONTAINER_DOCKER_BUILD_CONTEXT` - override Docker build context.
    - `TESTCONTAINER_DOCKER_BUILD_TARGET` - override Docker build target.
    """
    if image_id := os.getenv("TESTCONTAINER_IMAGE_ID"):
        yield image_id
    else:
        with EphemeralDockerImage(
            dockerfile=(Path(v) if (v := os.getenv("TESTCONTAINER_DOCKERFILE_PATH")) else None),
            context=(Path(v) if (v := os.getenv("TESTCONTAINER_DOCKER_BUILD_CONTEXT")) else None),
            target=os.getenv("TESTCONTAINER_DOCKER_BUILD_TARGET"),
            # Don't remove the image on teardown if it's used by other pytest-xdist workers in parallel.
            # The image will be eventually removed by the 'master' worker that exits last.
            remove_image_on_exit=not os.getenv("PYTEST_XDIST_WORKER"),
        ) as image:
            yield str(image.id)
