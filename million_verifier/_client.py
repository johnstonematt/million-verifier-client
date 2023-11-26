import csv
from io import StringIO
from typing import List, Optional
from datetime import datetime

from ._utils import (
    MV_SINGLE_API_URL,
    MV_BULK_API_URL,
    stringify,
    datetime_to_str,
    str_to_datetime,
    bool_to_int,
)
from ._enums import FileStatus, ReportStatus, Result, Quality
from ._client_core import CoreClient
from ._formats import (
    EmailVerification,
    FileInfo,
    ReportEntry,
    CreditsSummary,
    FileList,
    ActionResponse,
)


__all__ = ["MillionVerifierClient"]


class MillionVerifierClient(CoreClient):
    """
    Client for million-verifier API.
    """

    def verify_email_address(self, email: str, timeout: int = 20) -> EmailVerification:
        """
        Verify an email-address in real-time and get results in a second.
        Costs 1 credit.

        DOCS: https://developer.millionverifier.com/#operation/single-verification

        :param email: Email address to verify.
        :param timeout: Timeout to terminate connection. Must be between 2 and 60 (inclusive).
        :return: JSON data containing the email verification.
        """
        assert 2 <= timeout <= 60
        verification = self._get(
            url=f"{MV_SINGLE_API_URL}/api/v3",
            params={
                "api": self._api_key,
                "email": email,
                "timeout": timeout,
            },
        )
        verification["quality"] = Quality(verification["quality"])
        verification["result"] = Result(verification["result"])
        return verification

    def upload_file(self, file_path: str, file_name: Optional[str] = None) -> FileInfo:
        """
        Upload a file containing email addresses for verification.

        DOCS: https://developer.millionverifier.com/#operation/bulk-upload

        :param file_path: Path to the file.
        :param file_name: Name of the file, defaults to name of file specified in path.
        :return: JSON data confirming file upload and containing info regarding the file's status.
        """
        file_type = file_path.split(".")[-1]
        if file_type not in ("csv", "txt"):
            raise ValueError(
                f"Can only upload csv or txt files, {file_type} not supported."
            )

        if file_name is None:
            file_name = file_path.split("/")[-1]

        with open(file_path, "rb") as file:
            response = self._post(
                url=f"{MV_BULK_API_URL}/bulkapi/v2/upload",
                params={
                    "key": self._api_key,
                },
                files={
                    "file_contents": (file_name, file, "text/plain"),
                },
            )

        self._process_response(response=response)
        return self._parse_file_info(response=response)

    def get_file_info(self, file_id: int) -> FileInfo:
        """
        Get info for an uploaded file.

        DOCS: https://developer.millionverifier.com/#operation/bulk-fileinfo

        :param file_id: ID of the file.
        :return: JSON data containing file info.
        """
        response = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/v2/fileinfo",
            params={
                "key": self._api_key,
                "file_id": file_id,
            },
        )
        self._process_response(response=response, file_id=file_id)
        # formatting:
        return self._parse_file_info(response=response)

    def list_files(
        self,
        offset: int = 0,
        limit: int = 50,
        file_id: Optional[int | List[int]] = None,
        name: Optional[str] = None,
        status: Optional[FileStatus | List[FileStatus]] = None,
        updated_at_from: Optional[datetime] = None,
        updated_at_to: Optional[datetime] = None,
        create_date_from: Optional[datetime] = None,
        create_date_to: Optional[datetime] = None,
        percent_from: Optional[int] = None,
        percent_to: Optional[int] = None,
        has_error: Optional[bool] = None,
    ) -> FileList:
        """
        Get a list of files, according to the provided filters.

        DOCS: https://developer.millionverifier.com/#operation/bulk-filelist

        :param offset: Pagination offset.
        :param limit: Pagination limit, max 50.
        :param file_id: Filter for file IDs.
        :param name: Filter for file name.
        :param status: Filter for status.
        :param updated_at_from: Filter for files updated after this time.
        :param updated_at_to: Filter for files updated before this time.
        :param create_date_from: Filter for files created after this time.
        :param create_date_to: Filter for files created before this time.
        :param percent_from: Filter for files that have a progress greater than this.
        :param percent_to: Filter for files that have a progress less than this.
        :param has_error: Filter for files that either do or don't have errors.
        :return: ???
        """
        # verify pagination:
        assert offset >= 0
        assert 0 <= limit <= 50

        # verify time filters:
        if updated_at_from is not None and updated_at_to is not None:
            assert updated_at_from <= updated_at_to

        if create_date_from is not None and create_date_to is not None:
            assert create_date_from <= create_date_to

        # verify percent filters:
        for percent in (percent_from, percent_to):
            if percent is not None:
                assert 0 <= percent <= 100

        if percent_from is not None and percent_to is not None:
            assert percent_from <= percent_to

        response = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/v2/filelist",
            params={
                "key": self._api_key,
                "offset": offset,
                "limit": limit,
                "id": stringify(file_id),
                "name": name,
                "status": stringify(status),
                "updated_at_from": datetime_to_str(updated_at_from),
                "updated_at_to": datetime_to_str(updated_at_to),
                "createdate_from": datetime_to_str(create_date_from),
                "createdate_to": datetime_to_str(create_date_to),
                "percent_from": percent_from,
                "percent_to": percent_to,
                "has_error": has_error,
            },
        )
        self._process_response(response=response)
        return FileList(
            files=[
                self._parse_file_info(response=raw_info)
                for raw_info in response["files"]
            ],
            total=int(response["total"]),
        )

    def get_report(
        self,
        file_id: int,
        result_filter: Result = Result.ALL,
        status: Optional[ReportStatus | List[ReportStatus]] = None,
        include_free_domains: Optional[bool] = None,
        include_role_emails: Optional[bool] = None,
    ) -> List[ReportEntry]:
        """
        Get a report for the result of a file verification.

        DOCS: https://developer.millionverifier.com/#operation/bulk-download

        :param file_id: ID of the file of interest.
        :param result_filter: Filter to apply.
        :param status: Statuses to include (only for custom filter).
        :param include_free_domains: Whether to include free domains (only for custom filter).
        :param include_role_emails: Whether to include role emails (only for custom filter).
        :return: ???
        """
        if result_filter != Result.CUSTOM:
            assert status is None, "Must apply custom filter enum to filter statuses."
            assert (
                include_free_domains is None
            ), "Must apply custom filter enum to filter free domains."
            assert (
                include_role_emails is None
            ), "Must apply custom filter enum to filter role emails."

        csv_text = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/v2/download",
            params={
                "key": self._api_key,
                "file_id": file_id,
                "filter": result_filter,
                "statuses": stringify(status),
                "free": bool_to_int(include_free_domains),
                "role": bool_to_int(include_role_emails),
            },
            allow_text_return=True,
        )
        file = StringIO(csv_text)
        data, headings = [], []
        for csv_row in csv.reader(file):
            # if we are in the first row, and 'headings' is still an empty list, save the headings and then move on
            if not headings:
                headings = csv_row
                continue

            row = {}
            for key, val in zip(headings, csv_row):
                if key.lower() == "email":
                    row[key.lower()] = val

                elif key == "quality":
                    row[key] = Quality(val)

                elif key == "result":
                    row[key] = Result(val)

                elif key in ("free", "role"):
                    if val.lower() == "yes":
                        row[key] = True

                    elif val.lower() == "no":
                        row[key] = False

                    else:
                        raise ValueError(f"Unrecognised {key}: {val}")

                else:
                    row[key] = val

            # for type-hinting:
            data_row: ReportEntry = row
            data.append(data_row)

        return data

    def stop_a_file_in_progress(self, file_id: int) -> ActionResponse:
        """
        This will cancel a file that is currently in progress. The results for the already verified email
        addresses will be available for download in a few seconds.

        DOCS: https://developer.millionverifier.com/#operation/bulk-stop

        :param file_id: ID of the file to stop.
        :return: JSON dictionary indicating success.
        """
        response = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/stop",
            params={
                "key": self._api_key,
                "file_id": file_id,
            },
        )
        self._process_response(response=response, file_id=file_id)
        return response

    def delete_file(self, file_id: int) -> ActionResponse:
        """
        Delete a file that has been uploaded to the bulk api.

        DOCS: https://developer.millionverifier.com/#operation/bulk-delete

        :param file_id: ID of the file to delete.
        :return: JSON dictionary indicating success.
        """
        response = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/v2/delete",
            params={
                "key": self._api_key,
                "file_id": file_id,
            },
        )
        self._process_response(response=response, file_id=file_id)
        return response

    def check_credits(self) -> CreditsSummary:
        """
        Check the amount of available verification credits.

        DOCS: https://developer.millionverifier.com/#operation/api-credits

        :return: JSON dictionary detailing remaining credits.
        """
        response = self._get(
            url=f"{MV_SINGLE_API_URL}/api/v3/credits",
            params={
                "api": self._api_key,
            },
        )
        self._process_response(response=response)
        return response

    @staticmethod
    def _parse_file_info(response: dict) -> FileInfo:
        info = response.copy()
        info["file_id"] = int(info["file_id"])
        info["status"] = FileStatus(info["status"])
        info["updated_at"] = str_to_datetime(info["updated_at"])
        info["createdate"] = str_to_datetime(info["createdate"])
        return info

    @staticmethod
    def _process_response(response: dict, file_id: Optional[int] = None) -> None:
        """
        Check that the response is not an erroneous response and if so, raise the appropriate error.

        :param response: JSON response to process.
        :param file_id: File-ID of the request (if appropriate).
        :return: Nothing, the response is simply validated in place.
        """
        # TODO: flesh out this method to catch other cases and raise appropriate errors.
        if response.get("error") == "file_not_found":
            raise FileNotFoundError(
                f"No file with ID {file_id}. Response was: {response}"
            )
