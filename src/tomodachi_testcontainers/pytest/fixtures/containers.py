import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest

from tomodachi_testcontainers import EphemeralDockerImage


@pytest.fixture(scope="session")
def testcontainer_image() -> Generator[str, None, None]:
    # Test are running in parallel with pytest-xdist
    if os.getenv("PYTEST_XDIST_WORKER"):
        # Don't remove the image on teardown because it's used by other pytest-xdist workers at the same time
        with _testcontainer_image(remove_image_on_exit=False) as image_id:
            yield image_id
    # Tests are running without parallelization
    else:
        # No one else is using the image, remove it on teardown
        with _testcontainer_image(remove_image_on_exit=True) as image_id:
            yield image_id


@contextmanager
def _testcontainer_image(*, remove_image_on_exit: bool) -> Generator[str, None, None]:
    if image_id := os.getenv("TESTCONTAINER_IMAGE_ID"):
        yield image_id
    else:
        dockerfile = (
            Path(os.environ["TESTCONTAINER_DOCKERFILE_PATH"]) if os.getenv("TESTCONTAINER_DOCKERFILE_PATH") else None
        )
        context = (
            Path(os.environ["TESTCONTAINER_DOCKER_BUILD_CONTEXT"])
            if os.getenv("TESTCONTAINER_DOCKER_BUILD_CONTEXT")
            else None
        )
        target = os.getenv("TESTCONTAINER_DOCKER_BUILD_TARGET")
        with EphemeralDockerImage(
            dockerfile=dockerfile,
            context=context,
            target=target,
            remove_image_on_exit=remove_image_on_exit,
        ) as image:
            yield str(image.id)
