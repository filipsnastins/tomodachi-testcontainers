import asyncio
import contextlib
from typing import Iterator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    with contextlib.closing(asyncio.new_event_loop()) as loop:
        yield loop
