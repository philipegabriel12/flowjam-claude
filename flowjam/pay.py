"""Duration parsing and pay math. Pay is prorated to the second."""
import re
from decimal import Decimal, ROUND_HALF_UP

_HMS = re.compile(r"^\s*(\d+):([0-5]?\d)(?::([0-5]?\d))?\s*$")


def parse_duration(text: str) -> int:
    """'4:30:00' or '4:30' -> seconds."""
    m = _HMS.match(text)
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    h, mnt, s = int(m[1]), int(m[2]), int(m[3] or 0)
    return h * 3600 + mnt * 60 + s


def pay_for(seconds: int, rate: Decimal) -> Decimal:
    return (Decimal(seconds) * rate / Decimal(3600)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def fmt_duration(seconds: int) -> str:
    return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"
