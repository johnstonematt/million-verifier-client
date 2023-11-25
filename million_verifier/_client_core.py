from typing import Optional, Dict, Literal, Tuple, BinaryIO

from requests import Request, Session, HTTPError

from ._utils import APIException, Json


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
        data: Optional[Dict[str, Json]] = None,
        file: Optional[Tuple[str, Tuple[str, BinaryIO, str]]] = None,
    ) -> dict | list | str:
        # format parameters:
        parameters: dict = {} if params is None else params
        parameters = {key: val for key, val in parameters.items() if val is not None}

        request = Request(
            method=request_type,
            url=url,
            params=parameters,
            data=data,
            files=file,
        )
        response = self._session.send(
            request=request.prepare(),
        )
        # check for errors:
        try:
            response.raise_for_status()

        except HTTPError:
            raise APIException(response.text)

        return response.json()

    def _get(
        self,
        url: str,
        params: Optional[Dict[str, Json]] = None,
    ) -> dict | list | str:
        return self._make_request(
            request_type="GET",
            url=url,
            params=params,
        )

    def _post(
        self,
        url: str,
        params: Optional[Dict[str, Json]] = None,
        data: Optional[Dict[str, Json]] = None,
        file: Optional[Tuple[str, Tuple[str, BinaryIO, str]]] = None,
    ) -> dict:
        return self._make_request(
            request_type="POST",
            url=url,
            params=params,
            data=data,
            file=file,
        )

    def _delete(
        self,
        url: str,
        params: Optional[Dict[str, Json]] = None,
        data: Optional[Dict[str, Json]] = None,
    ) -> dict:
        return self._make_request(
            request_type="DELETE",
            url=url,
            params=params,
            data=data,
        )