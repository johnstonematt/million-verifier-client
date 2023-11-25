import os
from typing import get_type_hints

from dotenv import load_dotenv

from million_verifier import MillionVerifierClient, EmailVerification

# try both locations (such that the tests work, regardless of whether the tests are run from):
load_dotenv(".env.local")
load_dotenv("../.env.local")

# setup client:
client = MillionVerifierClient(api_key=os.getenv("MILLION_VERIFIER_API_KEY"))


def test_verify_email_address() -> None:
    verification = client.verify_email_address(
        email="johnstone.mattjames@gmail.com",
    )
    assert isinstance(verification, dict)
    types = get_type_hints(EmailVerification)
    for key, val_type in types.items():
        assert key in verification
        # remove ide type-check, as 'key' is a string, but it is expecting a literal (cos typed dict),
        # but we know it's correct:
        assert isinstance(verification[key], val_type)  # noqa
