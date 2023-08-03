from typing import Callable

from tenacity import AsyncRetrying, retry_if_not_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed


class _ProbeSucceeded(Exception):
    pass


async def probe_until(func: Callable, probe_interval: float = 0.1, stop_after: float = 3) -> None:
    """Run given function until it finished without exceptions or timeout is reached."""
    async for attempt in AsyncRetrying(
        wait=wait_fixed(probe_interval),
        stop=stop_after_delay(stop_after),
        reraise=True,
    ):
        with attempt:
            await func()


async def probe_during_interval(func: Callable, probe_interval: float = 0.1, stop_after: float = 3) -> None:
    """Run given function until timeout is reached and assert it always finished without exceptions."""
    try:
        async for attempt in AsyncRetrying(
            wait=wait_fixed(probe_interval),
            stop=stop_after_delay(stop_after),
            retry=retry_if_not_exception_type(AssertionError),
            reraise=True,
        ):
            with attempt:
                await func()
                raise _ProbeSucceeded
    except _ProbeSucceeded:
        pass
