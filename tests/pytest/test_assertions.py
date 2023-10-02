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


def test_logs_contain() -> None:
    mock_container = Mock(spec_set=DockerContainer)
    mock_container.get_logs = Mock(return_value=("stdout\n", "stderr\n"))

    assert_logs_contain(mock_container, "stdout")
    assert_logs_contain(mock_container, "stderr")

    with pytest.raises(AssertionError, match=r"Expected logs to contain: 'foo'"):
        assert_logs_contain(mock_container, "foo")


def test_logs_not_contain() -> None:
    mock_container = Mock(spec_set=DockerContainer)
    mock_container.get_logs = Mock(return_value=("stdout\n", "stderr\n"))

    assert_logs_not_contain(mock_container, "foo")

    with pytest.raises(AssertionError, match=r"Expected logs not to contain: 'stdout'"):
        assert_logs_not_contain(mock_container, "stdout")
    with pytest.raises(AssertionError, match=r"Expected logs not to contain: 'stderr'"):
        assert_logs_not_contain(mock_container, "stderr")
