from datetime import datetime, timedelta, timezone

UUID4_PATTERN = r"[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}"

DEFAULT_RANGE = timedelta(seconds=10)


def assert_datetime_within_range(value: datetime, range: timedelta = DEFAULT_RANGE) -> None:
    current_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)
    start_datetime = current_datetime - range
    end_datetime = current_datetime + range
    assert start_datetime <= value <= end_datetime  # nosec: B101
