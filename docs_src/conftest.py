import asyncio
from contextlib import closing
from typing import Iterator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    with closing(asyncio.new_event_loop()) as loop:
        yield loop
