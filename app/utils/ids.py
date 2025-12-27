"""Identifier helpers."""

from uuid import uuid4


def generate_uuid() -> str:
	"""Return a new UUID4 string."""

	return str(uuid4())


__all__ = ["generate_uuid"]
