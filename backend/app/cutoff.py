from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")

# Zamówienie na dany dzień przyjmujemy do 14:00 (czas warszawski) dnia poprzedniego.
# Godzina jest w czasie lokalnym, a nie w UTC: przesunięcie Warszawy względem UTC
# zmienia się z czasem letnim (UTC+2) i zimowym (UTC+1).
CUTOFF_TIME = time(14, 0)


def cutoff_for(delivery_date: date) -> datetime:
    """Moment, po którym nie da się już złożyć zamówienia na `delivery_date`."""
    order_day = delivery_date - timedelta(days=1)
    return datetime.combine(order_day, CUTOFF_TIME, tzinfo=WARSAW)


def is_before_cutoff(delivery_date: date, now: datetime) -> bool:
    """Czy w chwili `now` można jeszcze zamówić towar na `delivery_date`.

    `now` musi zawierać strefę czasową.
    """
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return now < cutoff_for(delivery_date)
