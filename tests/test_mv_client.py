import os
import time
import random
from datetime import datetime
from typing import Optional, List

from million_verifier import (
    EmailVerification,
    CreditsSummary,
    ReportEntry,
    FileInfo,
    FileList,
    ActionResponse,
    FileStatus,
)

from tests.utils import CLIENT, FREE_CLIENT, assert_typed_dict


def _random_file_id(files: FileList) -> int:
    random_index = random.randint(0, len(files["files"]) - 1)
    return files["files"][random_index]["file_id"]


# now that we've tested list_files, we can fetch some for ease of use:
all_files = CLIENT.list_files()


def test_actions() -> None:
    # such that it works regardless of where the test is run from:
    file_path = (
        "test-data/test-emails.txt"
        if os.path.exists("test-data/test-emails.txt")
        else "tests/test-data/test-emails.txt"
    )
    # upload and check that went well:
    upload_response = CLIENT.upload_file(file_path=file_path)
    assert_typed_dict(
        obj=upload_response,
        desired_type=FileInfo,
    )
    assert upload_response["file_name"] == "test-emails.txt"
    # sleep to make sure it went through:
    time.sleep(3)

    # now make sure the file is there:
    file_id = upload_response["file_id"]
    file_info_v1 = CLIENT.get_file_info(file_id=file_id)
    assert_typed_dict(
        obj=file_info_v1,
        desired_type=FileInfo,
    )
    assert file_info_v1["file_id"] == file_id

    # now stop:
    stop_response = CLIENT.stop_a_file_in_progress(file_id=file_id)
    assert_typed_dict(
        obj=stop_response,
        desired_type=ActionResponse,
        check_types=True,
    )
    assert stop_response["result"] == "ok"
    # sleep to make sure it went through:
    time.sleep(3)

    # check that it has indeed been stopped:
    file_info_v2 = CLIENT.get_file_info(file_id=file_id)
    assert_typed_dict(
        obj=file_info_v2,
        desired_type=FileInfo,
    )
    assert file_info_v2["file_id"] == file_id
    assert file_info_v2["status"] in (FileStatus.FINISHED, FileStatus.CANCELED)

    # now delete:
    delete_response = CLIENT.delete_file(file_id=file_id)
    assert_typed_dict(
        obj=delete_response,
        desired_type=ActionResponse,
    )
    assert delete_response["result"] == "ok"
