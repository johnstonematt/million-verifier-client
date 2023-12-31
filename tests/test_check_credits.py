from million_verifier import CreditsSummary

from tests.utils import CLIENT, assert_typed_dict


def test_check_credits() -> None:
    for _ in range(5):
        mv_credits = CLIENT.check_credits()
        assert_typed_dict(
            obj=mv_credits,
            desired_type=CreditsSummary,
        )
