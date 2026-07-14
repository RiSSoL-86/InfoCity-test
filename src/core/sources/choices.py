from enum import StrEnum


class Status(StrEnum):
    """Define source indexing states."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
