import os
from typing import Generator, cast

import pytest

from .. import WireMockContainer

try:
    from wiremock.constants import Config as WireMockConfig
except ImportError:
    WireMockConfig = None


@pytest.fixture(scope="session")
def wiremock_container() -> Generator[WireMockContainer, None, None]:
    image = os.getenv("WIREMOCK_TESTCONTAINER_IMAGE_ID", "wiremock/wiremock:latest")
    with WireMockContainer(image) as container:
        container = cast(WireMockContainer, container)
        if WireMockConfig is not None:
            WireMockConfig.base_url = f"{container.get_external_url()}/__admin/"
        yield container


@pytest.fixture()
def reset_wiremock_container_on_teardown(  # noqa: PT004
    wiremock_container: WireMockContainer,
) -> Generator[None, None, None]:
    """Deletes all stub mappings from WireMock after each test."""
    yield
    wiremock_container.delete_mappings()
