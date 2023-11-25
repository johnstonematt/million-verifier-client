from datetime import datetime
from typing import TypeAlias, Dict, TypeVar, List, Optional

__all__ = [
    "MV_SINGLE_API_URL",
    "MV_BULK_API_URL",
    "Json",
    "JsonDict",
    "APIException",
    "stringify",
    "datetime_to_str",
    "bool_to_int",
]

T = TypeVar("T")

MV_SINGLE_API_URL = "https://api.millionverifier.com"
MV_BULK_API_URL = "https://bulkapi.millionverifier.com"


Json: TypeAlias = dict | list | str | int | bool
JsonDict: TypeAlias = Dict[str, Json]


class APIException(Exception):
    """
    Raised from smartlead API errors.
    """


def stringify(i: Optional[T | List[T]]) -> Optional[str]:
    if i is None:
        return

    if isinstance(i, list):
        return ",".join(i)

    return str(i)


def datetime_to_str(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def bool_to_int(b: Optional[bool]) -> Optional[int]:
    if b is None:
        return

    return int(b)
