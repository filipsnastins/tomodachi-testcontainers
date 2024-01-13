import os
from pathlib import Path
from typing import Generator, cast

import pytest

from tomodachi_testcontainers import WireMockContainer
from tomodachi_testcontainers.utils import get_available_port

try:
    from wiremock.constants import Config as WireMockConfig
except ImportError:
    WireMockConfig = None


@pytest.fixture(scope="session")
def wiremock_container() -> Generator[WireMockContainer, None, None]:
    image = os.getenv("WIREMOCK_TESTCONTAINER_IMAGE_ID", "wiremock/wiremock:latest")
    mapping_stubs = os.getenv("WIREMOCK_TESTCONTAINER_MAPPING_STUBS")
    mapping_files = os.getenv("WIREMOCK_TESTCONTAINER_MAPPING_FILES")
    verbose = bool(os.getenv("WIREMOCK_TESTCONTAINER_VERBOSE"))
    with WireMockContainer(
        image=image,
        edge_port=get_available_port(),
        mapping_stubs=Path(mapping_stubs) if mapping_stubs else None,
        mapping_files=Path(mapping_files) if mapping_files else None,
        verbose=verbose,
    ) as container:
        container = cast(WireMockContainer, container)
        if WireMockConfig is not None:
            WireMockConfig.base_url = f"{container.get_external_url()}/__admin/"
        yield container


@pytest.fixture()
def _reset_wiremock_container_on_teardown(wiremock_container: WireMockContainer) -> Generator[None, None, None]:
    yield
    wiremock_container.delete_mappings()
