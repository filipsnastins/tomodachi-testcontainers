import contextlib
import os
from pathlib import Path
from typing import Generator

import docker.errors
import pytest

from tomodachi_testcontainers import EphemeralDockerImage


@pytest.fixture(scope="session")
def testcontainers_docker_image() -> Generator[str, None, None]:
    if os.getenv("PYTEST_XDIST_WORKER"):
        try:
            with _testcontainers_docker_image() as image_id:
                yield image_id
        except docker.errors.APIError as exc:
            if exc.response is not None:
                message = str(exc.response.json().get("message", ""))
                # Race condition when running tests in parallel -
                # multiple tests try to delete the same image at the same time.
                # The last test will succeed with deleting the image, the preceding tests will fail.
                if exc.response.status_code == 409 and "image is being used by running container" in message:
                    return
            raise
    else:
        with _testcontainers_docker_image() as image_id:
            yield image_id


@contextlib.contextmanager
def _testcontainers_docker_image() -> Generator[str, None, None]:
    if image_id := os.getenv("TOMODACHI_TESTCONTAINER_IMAGE_ID"):
        yield image_id
    else:
        dockerfile = (
            Path(os.environ["TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH"])
            if os.getenv("TOMODACHI_TESTCONTAINER_DOCKERFILE_PATH")
            else None
        )
        context = (
            Path(os.environ["TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT"])
            if os.getenv("TOMODACHI_TESTCONTAINER_DOCKER_BUILD_CONTEXT")
            else None
        )
        target = os.getenv("TOMODACHI_TESTCONTAINER_DOCKER_BUILD_TARGET")
        with EphemeralDockerImage(
            dockerfile=dockerfile,
            context=context,
            target=target,
        ) as image:
            yield str(image.id)
