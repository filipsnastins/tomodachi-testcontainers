import datetime
import re
import uuid
from unittest.mock import Mock

import pytest

from tomodachi_testcontainers import DockerContainer
from tomodachi_testcontainers.pytest.assertions import (
    UUID4_PATTERN,
    assert_datetime_within_range,
    assert_logs_contain,
    assert_logs_match_line_count,
    assert_logs_not_contain,
)


def test_match_uuid4_pattern() -> None:
    assert re.match(UUID4_PATTERN, str(uuid.uuid4()))

    assert not re.match(UUID4_PATTERN, "foo")


def test_assert_datetime_within_range() -> None:
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    assert_datetime_within_range(now - datetime.timedelta(seconds=9))
    assert_datetime_within_range(now + datetime.timedelta(seconds=10))

    with pytest.raises(AssertionError):
        assert_datetime_within_range(now - datetime.timedelta(seconds=10))
    with pytest.raises(AssertionError):
        assert_datetime_within_range(now + datetime.timedelta(seconds=11))


def test_assert_logs_contain() -> None:
    mock_container = Mock(spec_set=DockerContainer)
    mock_container.get_logs = Mock(return_value=(b"stdout\n", b"stderr\n"))

    assert_logs_contain(mock_container, "stdout")
    assert_logs_contain(mock_container, "stderr")

    with pytest.raises(AssertionError, match="Expected logs to contain: 'foo'"):
        assert_logs_contain(mock_container, "foo")


def test_assert_logs_not_contain() -> None:
    mock_container = Mock(spec_set=DockerContainer)
    mock_container.get_logs = Mock(return_value=(b"stdout\n", b"stderr\n"))

    assert_logs_not_contain(mock_container, "foo")

    with pytest.raises(AssertionError, match="Expected logs not to contain: 'stdout'"):
        assert_logs_not_contain(mock_container, "stdout")
    with pytest.raises(AssertionError, match="Expected logs not to contain: 'stderr'"):
        assert_logs_not_contain(mock_container, "stderr")


def test_assert_logs_match_line_count() -> None:
    mock_container = Mock(spec_set=DockerContainer)
    mock_container.get_logs = Mock(return_value=(b"stdout-1\nfoo\nstdout-2\nbar\n", b"foo\nstderr-1\nbar\nstderr-2\n"))

    assert_logs_match_line_count(mock_container, "stdout-", count=2)
    assert_logs_match_line_count(mock_container, "stderr-", count=2)
    with pytest.raises(AssertionError, match="Expected 'stdout-' to be contained in 1 lines, found 2 lines"):
        assert_logs_match_line_count(mock_container, "stdout-", count=1)
    with pytest.raises(AssertionError, match="Expected 'stderr-' to be contained in 1 lines, found 2 lines"):
        assert_logs_match_line_count(mock_container, "stderr-", count=1)
    with pytest.raises(AssertionError, match="Expected 'baz' to be contained in 2 lines, found 0 lines"):
        assert_logs_match_line_count(mock_container, "baz", count=2)
