from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from openpyxl import Workbook

MODULE_PATH = Path(__file__).resolve().parents[1] / "campaign_emailer.py"
SPEC = importlib.util.spec_from_file_location("campaign_emailer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


HEADER = [
    "ID",
    "Company Name",
    "Contact Name",
    "Phone",
    "Email Address",
    "Notes",
    "Emailed",
    "Date Emailed",
    "x9",
    "x10",
    "x11",
    "x12",
    "x13",
    "x14",
    "x15",
    "Status",
]


def make_sheet():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(HEADER)
    return workbook, worksheet


def test_clean_name_removes_parenthetical_notes():
    assert MODULE.clean_name("Michael Muto (owner)") == "Michael Muto"


def test_build_greeting_uses_first_name():
    greeting = MODULE.build_greeting(
        "michael muto",
        "Atlas Orthogonal Chiropractic",
    )
    assert greeting == "Hi Michael,"


def test_build_greeting_handles_doctor_titles():
    greeting = MODULE.build_greeting(
        "dr. jane smith",
        "Atlas Orthogonal Chiropractic",
    )
    assert greeting == "Hi Dr. Jane,"


def test_build_greeting_falls_back_to_company_team():
    greeting = MODULE.build_greeting(
        "Front Desk",
        "Atlas Orthogonal Chiropractic",
    )
    assert greeting == "Hi Atlas Orthogonal Chiropractic team,"


def test_build_greeting_falls_back_to_generic_when_company_is_unusable():
    assert MODULE.build_greeting(None, "Unknown") == "Hi there,"


def test_flag_helpers_cover_bool_string_numeric_and_blank_values():
    assert MODULE.flag_is_truthy(True)
    assert MODULE.flag_is_truthy("TRUE")
    assert MODULE.flag_is_truthy(1)
    assert not MODULE.flag_is_truthy("FALSE")

    assert MODULE.flag_is_falsey(False)
    assert MODULE.flag_is_falsey("FALSE")
    assert MODULE.flag_is_falsey(0)
    assert MODULE.flag_is_falsey(None)
    assert not MODULE.flag_is_falsey("TRUE")


def test_get_pending_rows_skips_invalid_email_and_limits_results():
    workbook, worksheet = make_sheet()
    worksheet.append(
        [
            1,
            "Atlas",
            "Michael Muto",
            "",
            "michael@example.com",
            "",
            False,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    worksheet.append(
        [
            2,
            "Beta Clinic",
            "Front Desk",
            "",
            "frontdesk@example.com",
            "",
            "FALSE",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    worksheet.append(
        [
            3,
            "Gamma",
            "Jane",
            "",
            "not-an-email",
            "",
            False,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    worksheet.append(
        [
            4,
            "Delta",
            "Dr. Adams",
            "",
            "dradams@example.com",
            "",
            True,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )

    pending = MODULE.get_pending_rows(worksheet, 2)

    assert [(row.row_num, row.company, row.contact, row.email) for row in pending] == [
        (2, "Atlas", "Michael Muto", "michael@example.com"),
        (3, "Beta Clinic", "Front Desk", "frontdesk@example.com"),
    ]
    workbook.close()


def test_build_tracker_lock_path_prefixes_tracker_filename():
    lock_path = MODULE.build_tracker_lock_path("/tmp/contacts-campaign-tracker.xlsx")
    assert lock_path == "/tmp/~$contacts-campaign-tracker.xlsx"
