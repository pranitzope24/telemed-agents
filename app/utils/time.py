"""Time utilities."""

from datetime import datetime, timezone


def current_timestamp_iso() -> str:
	"""Return the current UTC timestamp in ISO 8601 format."""

	return datetime.now(timezone.utc).isoformat()


__all__ = ["current_timestamp_iso"]
