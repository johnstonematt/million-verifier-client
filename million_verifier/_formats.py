from typing import TypedDict

from ._enums import Result, Quality


__all__ = [
    "EmailVerification",
]


class EmailVerification(TypedDict):
    """
    Email verification format.
    """

    email: str
    quality: Quality
    result: Result
    resultcode: int
    subresult: str
    free: bool
    role: bool
    didyoumean: str
    credits: int
    executiontime: int
    error: str
    livemode: bool
