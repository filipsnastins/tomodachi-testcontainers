from datetime import datetime, timedelta, timezone
from typing import Tuple

from tomodachi_testcontainers.containers.common import DockerContainer

UUID4_PATTERN = r"[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}"

DEFAULT_DATETIME_RANGE = timedelta(seconds=10)


def assert_datetime_within_range(value: datetime, range: timedelta = DEFAULT_DATETIME_RANGE) -> None:
    current_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)
    start_datetime = current_datetime - range
    end_datetime = current_datetime + range
    assert start_datetime <= value <= end_datetime  # nosec: B101


def assert_logs_contain(container: DockerContainer, expected: str) -> None:
    streams: Tuple[str, str] = container.get_logs()
    for stream in streams:
        if expected in stream:
            return
    raise AssertionError(f"Expected logs to contain: '{expected}'")


def assert_logs_not_contain(container: DockerContainer, expected: str) -> None:
    streams: Tuple[str, str] = container.get_logs()
    for stream in streams:
        if expected in stream:
            raise AssertionError(f"Expected logs not to contain: '{expected}'")
