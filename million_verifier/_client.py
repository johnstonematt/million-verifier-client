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
from ._enums import FileStatus, ReportStatus, Result, Quality, SubResult, ResultFilter
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

# limit can be found at https://developer.millionverifier.com/#operation/bulk-filelist
_PAGINATION_LIMIT = 50


class MillionVerifierClient(CoreClient):
    """
    Client for interacting with Million Verifier API.
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
        assert (
            2 <= timeout <= 60
        ), f"Verification timeout must be between 2 and 60 (inclusive), but received {timeout}."
        response = self._get(
            url=f"{MV_SINGLE_API_URL}/api/v3",
            params={
                "api": self._api_key,
                "email": email,
                "timeout": timeout,
            },
        )
        response["quality"] = Quality(response["quality"])
        response["result"] = Result(response["result"])
        response["subresult"] = SubResult(response["subresult"])
        return response

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
        # formatting:
        return self._parse_file_info(response=response)

    def _list_files(
        self,
        offset: int = 0,
        limit: int = _PAGINATION_LIMIT,
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
        # verify pagination:
        assert offset >= 0, f"offset must be positive, but received {offset}"
        assert (
            0 <= limit <= _PAGINATION_LIMIT
        ), f"limit must be between 0 and {_PAGINATION_LIMIT}, but received {limit}."

        # if we pass in a non-integer for file_id, it doesn't work, so we enforce integer:

        # verify time filters:
        if updated_at_from is not None and updated_at_to is not None:
            assert (
                updated_at_from <= updated_at_to
            ), f"updated_at_from ({updated_at_from}) must be before updated_at_to ({updated_at_to})."

        if create_date_from is not None and create_date_to is not None:
            assert (
                create_date_from <= create_date_to
            ), f"create_date_from ({create_date_from}) must be before create_date_to ({create_date_to})."

        # verify percent filters:
        for percent in (percent_from, percent_to):
            if percent is not None:
                assert (
                    0 <= percent <= 100
                ), "percentage must be between 1 and 100 (inclusive)"

        if percent_from is not None and percent_to is not None:
            assert (
                percent_from <= percent_to
            ), f"percent_from ({percent_from}) cannot be greater than percent_to ({percent_to})"

        # verify status:
        if status is not None:
            statuses = status if isinstance(status, list) else [status]
            for state in statuses:
                assert FileStatus.contains(
                    state
                ), f"{state} is not a valid FileStatus. Valid options are: {FileStatus.all()}"

        # there is an api bug where, if you set limit to 0, it acts as 50 (weird), so we handle that by making it 1:
        limit_to_use = 1 if limit == 0 else limit
        response = self._get(
            url=f"{MV_BULK_API_URL}/bulkapi/v2/filelist",
            params={
                "key": self._api_key,
                "offset": offset,
                "limit": limit_to_use,
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
        # if the limit was 0, we don't return any files, else parse all the files and return em:
        files = (
            []
            if limit == 0
            else [self._parse_file_info(raw_info) for raw_info in response["files"]]
        )
        return FileList(
            files=files,
            total=int(response["total"]),
        )

    def list_files(
        self,
        offset: int = 0,
        limit: Optional[int] = None,
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
        :param limit: Pagination limit, if > 50 then will fetch in batches of 50.
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
        :return: List of files that meet the provided requirements.
        """
        # set limit arbitrarily high if not specified:
        actual_limit = 1_000_000_000 if limit is None else limit
        # initialise loop variables:
        files_list = []
        files_acquired = 0
        while True:
            limit_to_use = min(
                actual_limit - files_acquired,
                _PAGINATION_LIMIT,
            )
            # need to do at least one call (even if limit_to_use = 0) to see what the total file number is:
            files = self._list_files(
                offset=offset + files_acquired,
                limit=limit_to_use,
                file_id=file_id,
                name=name,
                status=status,
                updated_at_from=updated_at_from,
                updated_at_to=updated_at_to,
                create_date_from=create_date_from,
                create_date_to=create_date_to,
                percent_from=percent_from,
                percent_to=percent_to,
                has_error=has_error,
            )
            # append and update:
            files_list.append(files)
            files_acquired += len(files["files"])
            # check exit conditions:
            if len(files["files"]) < limit_to_use or files_acquired >= actual_limit:
                break

        # combine all:
        all_files = []
        for file_list in files_list:
            all_files.extend(file_list["files"])

        return FileList(
            files=all_files,
            total=files_list[0]["total"],
        )

    def get_report(
        self,
        file_id: int,
        result_filter: ResultFilter = ResultFilter.ALL,
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
        :return: A csv-report (formatted as a list of dictionaries).
        """
        if result_filter != ResultFilter.CUSTOM:
            assert status is None, "Must apply custom filter enum to filter statuses."
            assert (
                include_free_domains is None
            ), "Must apply custom filter enum to filter free domains."
            assert (
                include_role_emails is None
            ), "Must apply custom filter enum to filter role emails."

        response = self._get(
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

        file = StringIO(response)
        data, headings = [], []
        for csv_row in csv.reader(file):
            # if we are in the first row, and 'headings' is still an empty list, save the headings and then move on
            if not headings:
                headings = csv_row
                continue

            row = {}
            for key, val in zip(headings, csv_row):
                if key == "quality":
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
        return response

    @staticmethod
    def _parse_file_info(response: dict) -> FileInfo:
        info = response.copy()
        info["file_id"] = int(info["file_id"])
        info["status"] = FileStatus(info["status"])
        info["updated_at"] = str_to_datetime(info["updated_at"])
        info["createdate"] = str_to_datetime(info["createdate"])
        return info
