__all__ = [
    "APIException",
    "InvalidAPIKey",
    "IPAddressBlocked",
    "InvalidParameterValue",
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


class InvalidParameterValue(APIException):
    """
    Raised when providing the API with an invalid parameter value (i.e., an enum that doesn't exist)
    """
