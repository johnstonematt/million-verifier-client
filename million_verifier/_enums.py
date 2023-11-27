from enum import Enum
from typing import Any, List, TypeVar, Type


__all__ = [
    "FileStatus",
    "Result",
    "ResultFilter",
    "SubResult",
    "ReportStatus",
    "Quality",
]


class _BaseEnum(str, Enum):
    """
    Base class for enums
    """

    @classmethod
    def all(cls: Type["T"]) -> List["T"]:
        return [cls(item) for item in cls]

    @classmethod
    def contains(cls, obj: Any) -> bool:
        for item in cls:
            if str(obj) == str(item):
                return True

        return False

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, (_BaseEnum, str)) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


T = TypeVar("T", bound=_BaseEnum)


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
    UNKNOWN = "unknown"


class Result(_BaseEnum):
    """
    Million Verifier verification results
    """

    OK = "ok"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DISPOSABLE = "disposable"
    REVERIFY = "reverify"


class Quality(_BaseEnum):
    """
    Million Verifier qualities.
    """

    RISKY = "risky"
    BAD = "bad"
    GOOD = "good"


class ResultFilter(_BaseEnum):
    """
    Result types that you can filter on when fetching reports.
    """

    OK = "ok"
    OK_AND_CATCH_ALL = "ok_and_catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    ALL = "all"
    CUSTOM = "custom"

    def allowed_results(self) -> List[Result]:
        match self:
            case ResultFilter.OK:
                return [Result.OK]

            case ResultFilter.OK_AND_CATCH_ALL:
                return [Result.OK, Result.CATCH_ALL]

            case ResultFilter.UNKNOWN:
                return [Result.UNKNOWN]

            case ResultFilter.INVALID:
                return [Result.INVALID, Result.DISPOSABLE]

            case ResultFilter.ALL | ResultFilter.CUSTOM:
                return Result.all()

            case _:
                raise NotImplementedError(
                    f"allowed_results not yet implemented for {self}"
                )

    def allowed_qualities(self) -> List[Quality]:
        match self:
            case ResultFilter.OK:
                return [Quality.GOOD]

            case ResultFilter.OK_AND_CATCH_ALL:
                return [Quality.GOOD, Quality.RISKY]

            case ResultFilter.UNKNOWN:
                return [Quality.RISKY]

            case ResultFilter.INVALID:
                return [Quality.BAD]

            case ResultFilter.ALL | ResultFilter.CUSTOM:
                return Quality.all()

            case _:
                raise NotImplementedError(
                    f"allowed_qualities not yet implemented for {self}."
                )


class SubResult(_BaseEnum):
    """
    Million Verifier verification sub-result.
    """

    UNKNOWN = "unknown"
    OK = "ok"
    INTERNAL_ERROR = "internal_error"
    INVALID_SYNTAX = "invalid_syntax"
    NO_LOCAL_IP_AVAILABLE = "no_local_available"
    DNS_SERVER_FAILURE = "dns_server_failure"
    DNS_SERVER_FAILED = "dns_server_failed"
    DNS_NO_MX = "dns_no_mx"
    DNS_NO_A = "dns_no_a"
    COULD_NOT_CONNECT = "could_not_connect"
    NO_CODE_IN_BANNER = "no_code_in_banner"
    INVALID_BANNER_CODE = "invalid_banner_code"
    NO_CODE_IN_EHLO_RESPONSE = "no_code_in_ehlo_response"
    NO_CODE_IN_HELO_RESPONSE = "no_code_in_helo_response"
    NO_CODE_IN_MAIL_FROM_RESPONSE = "no_code_in_mail_from_response"
    NO_CODE_IN_RCPT_TO_RESPONSE = "no_code_in_rcpt_to_response"
    IP_BLOCKED = "ip_blocked"
    NO_MAILBOX = "no_mailbox"
    MAILBOX_DISABLED = "mailbox_disabled"
    MAILBOX_FULL = "mailbox_full"
    GREYLISTED = "greylisted"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_TIMEOUT = "connection_timeout"
    CONNECTION_REFUSED = "connection_refused"
    CONNECTION_RESET_BY_PEER = "connection_reset_by_peer"
    CONNECTION_NO_ROUTE_TO_HOST = "connection_no_route_to_host"
    HOST_NOT_ACCEPT_INCOMING_MAIL = "host_not_accept_incoming_mail"
    MAIL_SERVICE_UNAVAILABLE = "mail_service_unavailable"
    BAD_DOMAIN = "bad_domain"
    DNS_ERROR = "dns_error"
    ANTI_SPAM_SYSTEM = "anti_spam_system"
    DNS_NO_DOMAIN = "dns_no_domain"
    DNS_REFUSED = "dns_refused"
    TIMEOUT_ERROR = "timeout_error"


class ReportStatus(_BaseEnum):
    """
    Million Verifier report status.
    """

    OK = "ok"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DISPOSABLE = "disposable"

    def allowed_results(self) -> List[Result]:
        match self:
            case ReportStatus.OK:
                return [Result.OK]

            case ReportStatus.CATCH_ALL:
                return [Result.CATCH_ALL]

            case ReportStatus.UNKNOWN:
                return [Result.UNKNOWN]

            case ReportStatus.INVALID:
                return [Result.INVALID]

            case ReportStatus.DISPOSABLE:
                return [Result.DISPOSABLE]

            case _:
                raise NotImplementedError(
                    f"allowed_results not yet implemented for {self}."
                )

    def allowed_qualities(self) -> List["Quality"]:
        match self:
            case ReportStatus.OK:
                return [Quality.GOOD]

            case ReportStatus.CATCH_ALL | ReportStatus.UNKNOWN:
                return [Quality.RISKY]

            case ReportStatus.INVALID | ReportStatus.DISPOSABLE:
                return [Quality.BAD]

            case _:
                raise NotImplementedError(
                    f"allowed_qualities not yet implemented for {self}."
                )
