"""Time utilities."""

from datetime import datetime, timezone


def timestamp_generator() -> str:
	"""Return the current UTC timestamp in ISO 8601 format."""

	return datetime.now(timezone.utc).isoformat()


__all__ = ["timestamp_generator"]
