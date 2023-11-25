from datetime import datetime
from typing import TypedDict, List

from ._enums import Result, Quality, FileStatus


__all__ = [
    "EmailVerification",
    "FileInfo",
    "ReportEntry",
    "CreditsSummary",
    "FileList",
    "ActionResponse",
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


class FileInfo(TypedDict):
    """
    Million Verifier file-info format
    """

    file_id: int
    file_name: str
    status: FileStatus
    unique_emails: int
    updated_at: datetime
    createdate: datetime
    percent: int
    total_rows: int
    verified: int
    unverified: int
    ok: int
    catch_all: int
    disposable: int
    invalid: int
    unknown: int
    reverify: int
    credit: int
    estimated_time_sec: int
    error: str


class ReportEntry(TypedDict):
    """
    Single line in a Million Verifier file report.
    """

    email: str
    quality: Quality
    result: Result
    free: bool
    role: bool


class CreditsSummary(TypedDict):
    """
    Million Verifier credits summary.
    """

    credits: int
    bulk_credits: int
    renewing_credits: int
    plan: int


class FileList(TypedDict):
    """
    List of files from Million Verifier
    """

    files: List[FileInfo]
    total: int


class ActionResponse(TypedDict):
    """
    Result for action-call to Million Verifier API.
    """

    result: str
