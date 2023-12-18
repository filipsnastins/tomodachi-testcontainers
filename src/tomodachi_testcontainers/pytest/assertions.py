from datetime import datetime, timedelta, timezone
from typing import Tuple, cast

from tomodachi_testcontainers import DockerContainer

UUID4_PATTERN = r"[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}"

DEFAULT_DATETIME_RANGE = timedelta(seconds=10)


def assert_datetime_within_range(value: datetime, range: timedelta = DEFAULT_DATETIME_RANGE) -> None:
    current_datetime = datetime.now(timezone.utc)
    start_datetime = current_datetime - range
    end_datetime = current_datetime + range
    assert start_datetime <= value <= end_datetime  # nosec: B101


def assert_logs_contain(container: DockerContainer, contains: str) -> None:
    stdout_and_stderr_logs = cast(Tuple[bytes, bytes], container.get_logs())
    for log in stdout_and_stderr_logs:
        if contains in log.decode():
            return
    raise AssertionError(f"Expected logs to contain: '{contains}'")


def assert_logs_not_contain(container: DockerContainer, contains: str) -> None:
    stdout_and_stderr_logs = cast(Tuple[bytes, bytes], container.get_logs())
    for log in stdout_and_stderr_logs:
        if contains in log.decode():
            raise AssertionError(f"Expected logs not to contain: '{contains}'")


def assert_logs_match_line_count(container: DockerContainer, contains: str, count: int) -> None:
    stdout_logs = cast(bytes, container.get_logs()[0])
    stderr_logs = cast(bytes, container.get_logs()[1])
    logs = "\n".join([stdout_logs.decode(), stderr_logs.decode()])
    matched_lines = [log for log in logs.splitlines() if contains in log]
    error_msg = f"Expected '{contains}' to be contained in {count} lines, found {len(matched_lines)} lines"
    assert len(matched_lines) == count, error_msg  # nosec: B101
