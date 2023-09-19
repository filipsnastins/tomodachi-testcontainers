import contextlib
from typing import Any, Callable

from tenacity import AsyncRetrying, RetryError, retry_unless_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed


async def probe_until(func: Callable, probe_interval: float = 0.1, stop_after: float = 3.0) -> Any:
    """Run given function until it finishes without exceptions."""
    result: Any = None
    async for attempt in AsyncRetrying(
        wait=wait_fixed(probe_interval),
        stop=stop_after_delay(stop_after),
        reraise=True,
    ):
        with attempt:
            result = await func()
    return result


async def probe_during_interval(func: Callable, probe_interval: float = 0.1, stop_after: float = 3.0) -> Any:
    """Run given function until timeout is reached and the function always finishes without exceptions."""
    result: Any = None
    with contextlib.suppress(RetryError):
        async for attempt in AsyncRetrying(
            wait=wait_fixed(probe_interval),
            stop=stop_after_delay(stop_after),
            retry=retry_unless_exception_type(BaseException),
            reraise=True,
        ):
            with attempt:
                result = await func()
    return result
