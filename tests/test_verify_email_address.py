from million_verifier import EmailVerification

from tests.utils import FREE_CLIENT, assert_typed_dict


def test_verify_email_address() -> None:
    for address in [
        "matthew@gmail.com",
        "mark@outlook.com",
        "luke@hotmail.com",
        "john@yahoo.com",
    ]:
        verification = FREE_CLIENT.verify_email_address(
            email=address,
        )
        assert_typed_dict(
            obj=verification,
            desired_type=EmailVerification,
        )
        assert verification["email"] == address
