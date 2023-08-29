from django.db.models import Func
from datetime import datetime, timedelta


class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 0)"


def str2bool(v):
    if isinstance(v, bool) or v is None:
        return v
    else:
        return v.lower() in ("yes", "true", "1")


def human_date_to_date(value: str | int) -> datetime:
    today = datetime.now().date()

    if isinstance(value, str):
        text = value.lower()
        if text == "yesterday":
            value = -1
        elif text == "today":
            value = 0
        elif text == "tomorrow":
            value = 1
        else:
            value - int(value)

    return today + timedelta(days=value)


def make_date(value: str) -> bool:
    try:
        value = datetime.strptime(value, "%Y-%m-%d").date()
        return value
    except ValueError:
        value = human_date_to_date(value)
        return value
