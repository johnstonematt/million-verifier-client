from enum import Enum
from typing import Any


__all__ = [
    "FileStatus",
    "ResultFilter",
    "ReportStatus",
]


class _BaseEnum(str, Enum):
    """
    Base class for enums
    """

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, (_BaseEnum, str)) and str(self) == str(other)


class FileStatus(_BaseEnum):
    """
    Million Verifier file statuses.
    """

    IN_PROGRESS = "in_progress"
    ERROR = "error"
    FINISHED = "finished"
    CANCELED = "canceled"
    PAUSED = "paused"
    IN_QUEUE_TO_START = "in_queue_to_start"


class ResultFilter(_BaseEnum):
    """
    Million Verifier report filters.
    """

    OK = "ok"
    OK_AND_CATCH_ALL = "ok_and_catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    ALL = "all"
    CUSTOM = "custom"


class ReportStatus(_BaseEnum):
    """
    Million Verifier report status.
    """

    OK = "ok"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DISPOSABLE = "disposable"
