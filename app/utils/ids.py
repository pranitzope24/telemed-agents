"""Identifier helpers."""

from uuid import uuid4


def uuid_generator() -> str:
	"""Return a new UUID4 string."""

	return str(uuid4())


__all__ = ["uuid_generator"]
