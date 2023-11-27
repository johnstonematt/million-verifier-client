import os
import random
from typing import TypeVar, get_type_hints, Type, Optional

from dotenv import load_dotenv

from million_verifier import MillionVerifierClient, FileList


# try both locations (such that the tests work, regardless of whether the tests are run from):
load_dotenv(".env.local")
load_dotenv("../.env.local")


__all__ = [
    "CLIENT",
    "FREE_CLIENT",
    "BAD_CLIENT",
    "assert_typed_dict",
    "find_random_index",
    "random_file_id",
]


# setup client:
CLIENT = MillionVerifierClient(api_key=os.getenv("MILLION_VERIFIER_API_KEY"))
FREE_CLIENT = MillionVerifierClient(api_key="API_KEY_FOR_TEST")
BAD_CLIENT = MillionVerifierClient(api_key="NOT-REAL-API-KEY")


T = TypeVar("T", bound=dict)


def assert_typed_dict(
    obj: T,
    desired_type: Type[T],
    check_types: bool = True,
    file_id: Optional[int] = None,
) -> None:
    assert isinstance(obj, dict)
    types = get_type_hints(desired_type)
    for key, val_type in types.items():
        assert key in obj, f"{key} not present. File ID: {file_id}"
        if check_types:
            assert isinstance(obj[key], val_type)


def find_random_index(obj: list) -> int:
    return random.randint(0, len(obj) - 1)


def random_file_id(files: FileList) -> int:
    random_index = find_random_index(obj=files["files"])
    return files["files"][random_index]["file_id"]
