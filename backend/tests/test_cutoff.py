from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from app.cutoff import is_before_cutoff

WAW = ZoneInfo("Europe/Warsaw")


def waw(*args) -> datetime:
    return datetime(*args, tzinfo=WAW)


def utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def test_summer_order_before_cutoff_is_accepted():
    assert is_before_cutoff(date(2027, 7, 15), waw(2027, 7, 14, 13, 59)) is True


def test_summer_order_at_cutoff_is_rejected():
    assert is_before_cutoff(date(2027, 7, 15), waw(2027, 7, 14, 14, 0)) is False


def test_summer_order_after_cutoff_is_rejected():
    assert is_before_cutoff(date(2027, 7, 15), waw(2027, 7, 14, 16, 30)) is False


def test_order_two_days_ahead_is_accepted():
    assert is_before_cutoff(date(2027, 7, 16), waw(2027, 7, 14, 18, 0)) is True


def test_winter_order_before_cutoff_is_accepted():
    assert is_before_cutoff(date(2027, 1, 15), waw(2027, 1, 14, 13, 30)) is True


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        is_before_cutoff(date(2027, 7, 15), datetime(2027, 7, 14, 12, 0))


def test_winter_order_at_cutoff_is_rejected():
    assert is_before_cutoff(date(2027, 1, 15), waw(2027, 1, 14, 14, 0)) is False


def test_last_microsecond_before_cutoff_is_accepted():
    assert is_before_cutoff(date(2027, 1, 15), waw(2027, 1, 14, 13, 59, 59, 999999)) is True


def test_order_for_today_is_rejected():
    assert is_before_cutoff(date(2027, 7, 14), waw(2027, 7, 14, 8, 0)) is False


# Zmiana czasu w 2027: 28.03 (zimowy -> letni) i 31.10 (letni -> zimowy).
# Dzień zamówienia to sam dzień zmiany, więc przesunięcie UTC jest inne niż dzień wcześniej.
@pytest.mark.parametrize(
    ("delivery", "now", "expected"),
    [
        (date(2027, 3, 29), waw(2027, 3, 28, 13, 59), True),
        (date(2027, 3, 29), waw(2027, 3, 28, 14, 0), False),
        (date(2027, 11, 1), waw(2027, 10, 31, 13, 59), True),
        (date(2027, 11, 1), waw(2027, 10, 31, 14, 0), False),
    ],
)
def test_cutoff_on_dst_change_day(delivery, now, expected):
    assert is_before_cutoff(delivery, now) is expected


# `now` z serwera zwykle przychodzi w UTC – 14:00 w Warszawie to 12:00 UTC latem i 13:00 UTC zimą.
@pytest.mark.parametrize(
    ("delivery", "now", "expected"),
    [
        (date(2027, 7, 15), utc(2027, 7, 14, 11, 59), True),
        (date(2027, 7, 15), utc(2027, 7, 14, 12, 0), False),
        (date(2027, 1, 15), utc(2027, 1, 14, 12, 59), True),
        (date(2027, 1, 15), utc(2027, 1, 14, 13, 0), False),
    ],
)
def test_cutoff_with_utc_now(delivery, now, expected):
    assert is_before_cutoff(delivery, now) is expected
