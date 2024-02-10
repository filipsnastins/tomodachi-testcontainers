"""Asynchronous probes (sampling) for testing asynchronous systems.

Inspired by [Awaitility](https://github.com/awaitility/awaitility) and [busypie](https://github.com/rockem/busypie).
"""

import asyncio
from contextlib import suppress
from typing import Any, Awaitable, Callable, TypeVar, Union, cast, overload

from tenacity import AsyncRetrying, RetryError, retry_unless_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

T = TypeVar("T")


@overload
async def probe_until(
    probe: Callable[[], Awaitable[T]],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T: ...  # pragma: no cover


@overload
async def probe_until(
    probe: Callable[[], T],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T: ...  # pragma: no cover


async def probe_until(
    probe: Union[Callable[[], Awaitable[T]], Callable[[], T]],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T:
    """Run given function until it finishes without exceptions.

    Given function can be a regular synchronous function or an asynchronous function.
    """
    result: Any = None
    async for attempt in AsyncRetrying(
        wait=wait_fixed(probe_interval),
        stop=stop_after_delay(stop_after),
        reraise=True,
    ):
        with attempt:
            result = probe()
            if asyncio.iscoroutine(result):
                result = await result
    return cast(T, result)


@overload
async def probe_during_interval(
    probe: Callable[[], Awaitable[T]],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T: ...  # pragma: no cover


@overload
async def probe_during_interval(
    probe: Callable[[], T],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T: ...  # pragma: no cover


async def probe_during_interval(
    probe: Callable[[], Union[Awaitable[T], T]],
    probe_interval: float = 0.1,
    stop_after: float = 3.0,
) -> T:
    """Run given function until timeout is reached and the function always finishes without exceptions.

    Given function can be a regular synchronous function or an asynchronous function.
    """
    result: Any = None
    with suppress(RetryError):
        async for attempt in AsyncRetrying(
            wait=wait_fixed(probe_interval),
            stop=stop_after_delay(stop_after),
            retry=retry_unless_exception_type(BaseException),
            reraise=True,
        ):
            with attempt:
                result = probe()
                if asyncio.iscoroutine(result):
                    result = await result
    return cast(T, result)
