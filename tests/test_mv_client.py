import os
import time
import random
from typing import get_type_hints, Type, TypeVar

from dotenv import load_dotenv

from million_verifier import (
    MillionVerifierClient,
    EmailVerification,
    CreditsSummary,
    ReportEntry,
    FileInfo,
    FileList,
    ActionResponse,
    FileStatus,
)

# try both locations (such that the tests work, regardless of whether the tests are run from):
load_dotenv(".env.local")
load_dotenv("../.env.local")

# setup client:
client = MillionVerifierClient(api_key=os.getenv("MILLION_VERIFIER_API_KEY"))
free_client = MillionVerifierClient(api_key="API_KEY_FOR_TEST")

T = TypeVar("T", bound=dict)


def _assert_typed_dict(obj: T, desired_type: Type[T], check_types: bool = True) -> None:
    assert isinstance(obj, dict)
    types = get_type_hints(desired_type)
    for key, val_type in types.items():
        assert key in obj
        if check_types:
            assert isinstance(obj[key], val_type)


def _random_file_id(files: FileList) -> int:
    random_index = random.randint(0, len(files["files"]) - 1)
    return files["files"][random_index]["file_id"]


def test_verify_email_address() -> None:
    verification = free_client.verify_email_address(
        email="john@gmail.com",
    )
    _assert_typed_dict(
        obj=verification,
        desired_type=EmailVerification,
    )


def test_check_credits() -> None:
    mv_credits: dict = client.check_credits()
    _assert_typed_dict(
        obj=mv_credits,
        desired_type=CreditsSummary,
    )


def test_list_files() -> None:
    files = client.list_files()
    # check_types = False because python can't check isinstance(obj, List[type])
    _assert_typed_dict(
        obj=files,
        desired_type=FileList,
        check_types=False,
    )
    for file in files["files"]:
        _assert_typed_dict(
            obj=file,
            desired_type=FileInfo,
        )

    assert len(files["files"]) <= files["total"]


# now that we've tested list_files, we can fetch some for ease of use:
all_files = client.list_files()


def test_get_file_info() -> None:
    file_id = _random_file_id(files=all_files)
    file_info = client.get_file_info(file_id=file_id)
    _assert_typed_dict(
        obj=file_info,
        desired_type=FileInfo,
    )
    assert file_info["file_id"] == file_id


def test_get_report() -> None:
    file_id = _random_file_id(files=all_files)
    report = client.get_report(file_id=file_id)
    assert isinstance(report, list)
    for row in report:
        _assert_typed_dict(
            obj=row,
            desired_type=ReportEntry,
        )


def test_actions() -> None:
    # such that it works regardless of where the test is run from:
    file_path = (
        "test-data/test-emails.txt"
        if os.path.exists("test-data/test-emails.txt")
        else "tests/test-data/test-emails.txt"
    )
    # upload and check that went well:
    upload_response = client.upload_file(file_path=file_path)
    _assert_typed_dict(
        obj=upload_response,
        desired_type=FileInfo,
    )
    assert upload_response["file_name"] == "test-emails.txt"
    # sleep to make sure it went through:
    time.sleep(3)

    # now make sure the file is there:
    file_id = upload_response["file_id"]
    file_info_v1 = client.get_file_info(file_id=file_id)
    _assert_typed_dict(
        obj=file_info_v1,
        desired_type=FileInfo,
    )
    assert file_info_v1["file_id"] == file_id

    # now stop:
    stop_response = client.stop_a_file_in_progress(file_id=file_id)
    _assert_typed_dict(
        obj=stop_response,
        desired_type=ActionResponse,
        check_types=True,
    )
    assert stop_response["result"] == "ok"
    # sleep to make sure it went through:
    time.sleep(3)

    # check that it has indeed been stopped:
    file_info_v2 = client.get_file_info(file_id=file_id)
    _assert_typed_dict(
        obj=file_info_v2,
        desired_type=FileInfo,
    )
    assert file_info_v2["file_id"] == file_id
    assert file_info_v2["status"] in (FileStatus.FINISHED, FileStatus.CANCELED)

    # now delete:
    delete_response = client.delete_file(file_id=file_id)
    _assert_typed_dict(
        obj=delete_response,
        desired_type=ActionResponse,
    )
    assert delete_response["result"] == "ok"
