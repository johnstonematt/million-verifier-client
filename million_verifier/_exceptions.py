__all__ = [
    "APIException",
    "InvalidAPIKey",
    "IPAddressBlocked",
]


class APIException(Exception):
    """
    Raised from Million Verifier API errors.
    """


class InvalidAPIKey(APIException):
    """
    Raised when using an invalid api key.
    """


class IPAddressBlocked(APIException):
    """
    Raised when using a blocked IP address
    """
