import random
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

import pytest

from million_verifier import (
    FileList,
    FileInfo,
    FileStatus,
    ReportEntry,
    ReportStatus,
    ResultFilter,
    InvalidParameterValue,
)

from tests.utils import CLIENT, assert_typed_dict


def test_list_files() -> None:
    files = CLIENT.list_files()
    # check_types = False because python can't check isinstance(obj, List[type])
    assert_typed_dict(
        obj=files,
        desired_type=FileList,
        check_types=False,
    )
    for file in files["files"]:
        assert_typed_dict(
            obj=file,
            desired_type=FileInfo,
        )

    assert len(files["files"]) == files["total"]


# now that we know list_files works (to some degree), let's get all files for ease of use:
_all_files = CLIENT.list_files()
ALL_FILES = _all_files["files"]


def test_list_files_status_filter() -> None:
    for status in FileStatus.all():
        # providing 'unknown' filter does not filter at all:
        if status == FileStatus.UNKNOWN:
            continue

        files = CLIENT.list_files(status=status)
        for file in files["files"]:
            assert file["status"] == status


def test_list_files_fuzz_filters() -> None:
    for _ in range(10):
        (
            file_id,
            name,
            status,
            updated_at_from,
            updated_at_to,
            create_date_from,
            create_date_to,
            percent_from,
            percent_to,
            has_error,
        ) = _get_random_list_files_filters()

        files = CLIENT.list_files(
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
        assert_typed_dict(
            obj=files,
            desired_type=FileList,
            check_types=False,
        )
        for file in files["files"]:
            assert_typed_dict(
                obj=file,
                desired_type=FileInfo,
            )
            _test_single_case_list_files_filters(
                file=file,
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


def test_get_file_info() -> None:
    for _ in range(10):
        file_id = _random_file_id()
        file_info = CLIENT.get_file_info(file_id=file_id)
        assert_typed_dict(
            obj=file_info,
            desired_type=FileInfo,
            file_id=file_id,
        )
        assert file_info["file_id"] == file_id


def test_get_report() -> None:
    file_id = _random_file_id()
    report = CLIENT.get_report(file_id=file_id)
    assert isinstance(report, list)
    for row in report:
        assert_typed_dict(
            obj=row,
            desired_type=ReportEntry,
            file_id=file_id,
        )


def test_get_report_fuzz_filters() -> None:
    for _ in range(10):
        # randomly generate arguments:
        file_id = _random_file_id()
        (
            result_filter,
            status,
            include_free_domains,
            include_role_emails,
        ) = _get_random_report_filters()
        # fetch report:
        report = CLIENT.get_report(
            file_id=file_id,
            result_filter=result_filter,
            status=status,
            include_free_domains=include_free_domains,
            include_role_emails=include_role_emails,
        )
        assert isinstance(report, list)
        for row in report:
            assert_typed_dict(
                obj=row,
                desired_type=ReportEntry,
                file_id=file_id,
            )
            _test_get_report_filters(
                report_row=row,
                result_filter=result_filter,
                status=status,
                include_free_domains=include_free_domains,
                include_role_emails=include_role_emails,
            )


def test_file_not_found() -> None:
    fake_file_id = 2 * max([file["file_id"] for file in ALL_FILES])
    with pytest.raises(FileNotFoundError):
        CLIENT.get_file_info(file_id=fake_file_id)

    with pytest.raises(FileNotFoundError):
        CLIENT.get_report(file_id=fake_file_id)

    with pytest.raises(FileNotFoundError):
        CLIENT.stop_a_file_in_progress(file_id=fake_file_id)

    with pytest.raises(FileNotFoundError):
        CLIENT.delete_file(file_id=fake_file_id)


def test_get_report_incorrect_parameter() -> None:
    file_id = _random_file_id()
    with pytest.raises(InvalidParameterValue):
        CLIENT.get_report(file_id=file_id, result_filter="NOT_A_FILTER")


def _test_single_case_list_files_filters(
    file: FileInfo,
    file_id: Optional[int | List[int]],
    name: Optional[str],
    status: Optional[FileStatus | List[FileStatus]],
    updated_at_from: Optional[datetime],
    updated_at_to: Optional[datetime],
    create_date_from: Optional[datetime],
    create_date_to: Optional[datetime],
    percent_from: Optional[int],
    percent_to: Optional[int],
    has_error: Optional[bool],
) -> None:
    if file_id is not None:
        if isinstance(file_id, int):
            assert file["file_id"] == file_id

        else:
            assert file["file_id"] in file_id

    if name is not None:
        assert name.lower() in file["file_name"].lower()

    if status is not None:
        if isinstance(status, FileStatus):
            # when filtering by unknown, they allow anything to return
            assert file["status"] == status or status == FileStatus.UNKNOWN

        else:
            assert file["status"] in status

    if updated_at_from is not None:
        assert file["updated_at"] >= updated_at_from

    if updated_at_to is not None:
        assert file["updated_at"] <= updated_at_to

    if create_date_from is not None:
        assert file["createdate"] >= create_date_from

    if create_date_to is not None:
        assert file["createdate"] <= create_date_to

    if percent_from is not None:
        assert file["percent"] >= percent_from

    if percent_to is not None:
        assert file["percent"] <= percent_to

    if has_error is not None:
        if has_error:
            assert file["error"]

        else:
            assert not file["error"]


def _test_get_report_filters(
    report_row: ReportEntry,
    result_filter: ResultFilter,
    status: Optional[ReportStatus | List[ReportStatus]],
    include_free_domains: Optional[bool],
    include_role_emails: Optional[bool],
) -> None:
    # vanilla result filter:
    assert report_row["result"] in result_filter.allowed_results()
    assert report_row["quality"] in result_filter.allowed_qualities()

    # custom filter:
    if result_filter == ResultFilter.CUSTOM:
        if status is not None:
            # compile all allowed results and qualities based on status filters:
            statuses = status if isinstance(status, list) else [status]
            allowed_results, allowed_qualities = set(), set()
            for state in statuses:
                allowed_results |= set(state.allowed_results())
                allowed_qualities |= set(state.allowed_qualities())

            assert report_row["result"] in allowed_results
            assert report_row["quality"] in allowed_qualities

        if include_free_domains is not None:
            assert report_row["free"] == include_free_domains

        if include_role_emails is not None:
            assert report_row["role"] == include_role_emails


def _get_random_report_filters() -> Tuple[
    ResultFilter,
    Optional[ReportStatus | List[ReportStatus]],
    Optional[bool],
    Optional[bool],
]:
    # 50/50 between custom or random:
    if random.randint(0, 1):
        random_index = random.randint(0, len(ResultFilter.all()) - 1)
        result_filter = ResultFilter.all()[random_index]

    else:
        result_filter = ResultFilter.CUSTOM

    # now do the rest:
    status: Optional[ReportStatus | List[ReportStatus]] = None
    include_free_domains: Optional[bool] = None
    include_role_emails: Optional[bool] = None
    # only set them if we're using a custom filter:
    if result_filter == ResultFilter.CUSTOM:
        # status:
        if random.randint(0, 1):
            # singular or list:
            if random.randint(0, 1):
                status = random.sample(
                    population=ReportStatus.all(),
                    k=random.randint(1, len(ReportStatus.all())),
                )

            else:
                random_index = random.randint(0, len(ReportStatus.all()) - 1)
                status = ReportStatus.all()[random_index]

        # include_free_domain:
        if random.randint(0, 1):
            include_free_domains = bool(random.randint(0, 1))

        # include_role_emails:
        if random.randint(0, 1):
            include_role_emails = bool(random.randint(0, 1))

    return (
        result_filter,
        status,
        include_free_domains,
        include_role_emails,
    )


def _get_random_list_files_filters() -> Tuple[
    Optional[int | List[int]],
    Optional[str],
    Optional[FileStatus | List[FileStatus]],
    Optional[datetime],
    Optional[datetime],
    Optional[datetime],
    Optional[datetime],
    Optional[int],
    Optional[int],
    Optional[bool],
]:
    # file ID:
    if random.randint(0, 1):
        # single or list:
        all_file_ids = [file["file_id"] for file in ALL_FILES]
        if random.randint(0, 1):
            real_sample_size = random.randint(0, len(all_file_ids))
            real_file_ids: List[int] = random.sample(
                population=all_file_ids,
                k=real_sample_size,
            )
            # add some fake IDs (lol) as well:
            fake_sample_size = random.randint(0, real_sample_size)
            fake_file_ids = [
                random.randint(0, max(all_file_ids)) for _ in range(fake_sample_size)
            ]
            file_id = list(set(real_file_ids + fake_file_ids))

        else:
            file_id = all_file_ids[random.randint(0, len(all_file_ids) - 1)]

    else:
        file_id = None

    # name:
    if random.randint(0, 1):
        name = ["csv", "nt", "a", "ck"][random.randint(0, 3)]

    else:
        name = None

    # status:
    if random.randint(0, 1):
        statuses = FileStatus.all()
        if random.randint(0, 1):
            status = random.sample(
                population=statuses,
                k=random.randint(0, len(statuses) - 1),
            )

        else:
            status = FileStatus.all()[random.randint(0, len(statuses) - 1)]

    else:
        status = None

    # updated_at:
    updated_at_from, updated_at_to = _get_random_dates()

    # create_date:
    create_date_from, create_date_to = _get_random_dates()

    # percent_from:
    if random.randint(0, 1):
        percent_from = random.randint(0, 100)

    else:
        percent_from = None

    # percent_to:
    if random.randint(0, 1):
        start_percent = 0 if percent_from is None else percent_from
        percent_to = random.randint(start_percent, 100)

    else:
        percent_to = None

    # has_error:
    if random.randint(0, 1):
        has_error = bool(random.randint(0, 1))

    else:
        has_error = None

    return (
        file_id,
        name,
        status,
        updated_at_from,
        updated_at_to,
        create_date_from,
        create_date_to,
        percent_from,
        percent_to,
        has_error,
    )


def _get_random_dates() -> (Optional[datetime], Optional[datetime]):
    now = datetime.now()
    start_date = min(file["updated_at"] for file in ALL_FILES)
    # from_date:
    if random.randint(0, 1):
        delta = (now - start_date) + timedelta(days=1)
        from_date = now - (random.random() * delta)

    else:
        from_date = None

    # to_date:
    if random.randint(0, 1):
        first_allowed_date = start_date if from_date is None else from_date
        delta = datetime.now() - first_allowed_date
        to_date = datetime.now() - (random.random() * delta)

    else:
        to_date = None

    return from_date, to_date


def _random_file_id() -> int:
    return ALL_FILES[random.randint(0, len(ALL_FILES) - 1)]["file_id"]
