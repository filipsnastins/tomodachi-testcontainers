import datetime
import re
import uuid

import pytest

from tomodachi_testcontainers.pytest.assertions import UUID4_PATTERN, assert_datetime_within_range


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
