from datetime import datetime, timezone


def utc_now() -> datetime:
    """Current UTC time as a naive datetime (matches existing DateTime columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
