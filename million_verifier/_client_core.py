import re
from json import JSONDecodeError
from typing import Optional, Dict, Literal, Tuple, BinaryIO

from requests import Request, Session, HTTPError

from ._utils import Json
from ._exceptions import (
    APIException,
    IPAddressBlocked,
    InvalidAPIKey,
    InvalidParameterValue,
)


__all__ = [
    "CoreClient",
]


class CoreClient:
    """
    Base class for smartlead client.
    """

    def __init__(self, api_key: str) -> None:
        if not isinstance(api_key, str):
            raise ValueError(
                f"API-key must be a string, can't be of type {type(api_key).__name__}."
            )

        self._api_key = api_key
        self._session = Session()

    def _make_request(
        self,
        request_type: Literal["GET", "POST", "DELETE"],
        url: str,
        params: Optional[Dict[str, Json]] = None,
        files: Optional[Dict[str, Tuple[str, BinaryIO, str]]] = None,
        allow_text_return: bool = False,
    ) -> dict | list | str:
        # format parameters:
        parameters: dict = {} if params is None else params
        parameters = {key: val for key, val in parameters.items() if val is not None}

        request = Request(
            method=request_type,
            url=url,
            params=parameters,
            files=files,
        )
        response = self._session.send(
            request=request.prepare(),
        )
        # check for errors:
        try:
            response.raise_for_status()

        except HTTPError:
            raise APIException(response.text)

        try:
            result = response.json()

        except JSONDecodeError:
            if allow_text_return:
                result = response.text

            else:
                raise

        self._process_response(response=result)
        return result

    def _get(
        self,
        url: str,
        params: Optional[Dict[str, Json]] = None,
        allow_text_return: bool = False,
    ) -> dict | str:
        return self._make_request(
            request_type="GET",
            url=url,
            params=params,
            allow_text_return=allow_text_return,
        )

    def _post(
        self,
        url: str,
        params: Optional[Dict[str, Json]] = None,
        files: Optional[Dict[str, Tuple[str, BinaryIO, str]]] = None,
    ) -> dict:
        return self._make_request(
            request_type="POST",
            url=url,
            params=params,
            files=files,
        )

    @staticmethod
    def _process_response(response: dict | str) -> None:
        """
        Check that the response is not an erroneous response and if so, raise the appropriate error.

        :param response: JSON response to process.
        :return: Nothing, the response is simply validated in place.
        """
        # check that we got an error that is not just an empty string:
        if (
            isinstance(response, dict)
            and isinstance(response.get("error"), str)
            and response["error"]
        ):
            error: str = response["error"]
            if error.lower() == "file_not_found":
                raise FileNotFoundError(f"File ID not found. Response was: {response}")

            if error.lower() == "apikey not found":
                raise InvalidAPIKey(f"Invalid API key. Response was {response}")

            if error.lower() == "ip address blocked":
                raise IPAddressBlocked(f"IP address blocked. Response was {response}")

            if re.match(r"unsupported \w+ value", error):
                raise InvalidParameterValue(
                    f"Invalid parameter. Response was {response}"
                )

            raise APIException(
                f"Unknown error from MV API: '{error}'. Response was {response}"
            )
