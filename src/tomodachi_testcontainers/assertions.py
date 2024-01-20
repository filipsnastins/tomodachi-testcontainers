from datetime import datetime, timedelta, timezone
from typing import Tuple, cast

from . import DockerContainer

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
    raise AssertionError(f"Expected logs to contain: '{contains}'; logs: {stdout_and_stderr_logs}")  # noqa: E702


def assert_logs_not_contain(container: DockerContainer, contains: str) -> None:
    stdout_and_stderr_logs = cast(Tuple[bytes, bytes], container.get_logs())
    for log in stdout_and_stderr_logs:
        if contains in log.decode():
            raise AssertionError(
                f"Expected logs not to contain: '{contains}'; logs: {stdout_and_stderr_logs}"  # noqa: E702
            )


def assert_logs_match_line_count(container: DockerContainer, contains: str, count: int) -> None:
    stdout_logs = cast(bytes, container.get_logs()[0])
    stderr_logs = cast(bytes, container.get_logs()[1])
    stdout_and_stderr_logs = "\n".join([stdout_logs.decode(), stderr_logs.decode()])

    matched_lines = [log for log in stdout_and_stderr_logs.splitlines() if contains in log]
    error_msg = (
        f"Expected '{contains}' to be contained in {count} lines, found {len(matched_lines)} lines"  # noqa: E702
        f"; logs: {stdout_and_stderr_logs}"  # noqa: E702
    )
    assert len(matched_lines) == count, error_msg  # nosec: B101
