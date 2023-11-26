import os
import time

import pytest
from dotenv import load_dotenv

from million_verifier import (
    MillionVerifierClient,
    APIException,
    InvalidAPIKey,
    IPAddressBlocked,
)


# try both locations (such that the tests work, regardless of whether the tests are run from):
load_dotenv(".env.local")
load_dotenv("../.env.local")


# setup client:
client = MillionVerifierClient(api_key=os.getenv("MILLION_VERIFIER_API_KEY"))
free_client = MillionVerifierClient(api_key="API_KEY_FOR_TEST")
bad_client = MillionVerifierClient(api_key="NOT-REAL-API-KEY")


def test_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        client.get_file_info(0)
        time.sleep(0.5)

    with pytest.raises(FileNotFoundError):
        client.get_report(0)
        time.sleep(0.5)

    with pytest.raises(FileNotFoundError):
        client.stop_a_file_in_progress(0)
        time.sleep(0.5)

    with pytest.raises(FileNotFoundError):
        client.delete_file(0)
        time.sleep(0.5)


def test_bad_api_key() -> None:

    with pytest.raises((InvalidAPIKey, IPAddressBlocked)):
        bad_client.verify_email_address("fake-email")
