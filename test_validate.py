# test_validate.py
# ─────────────────────────────────────────────────────────────────────────────
# Tests for the validation logic in validate.py.
#
# These tests verify that the PROGRAM behaves correctly — they do not check
# your actual metadata.py or schema.py data.
#
# When to run:
#   Only if you modify validate.py or pack_bundle.py.
#   Not needed for normal daily workflow (pack_bundle.py handles that).
#
# How to run:
#   python test_validate.py
# ─────────────────────────────────────────────────────────────────────────────

import sys
import tempfile
from pathlib import Path

import validate as v


# ── Minimal test runner (no pytest needed) ────────────────────────────────────

passed = 0
failed = 0

def expect_errors(label, errors, expected_fragment):
    """Assert that at least one error contains the expected fragment."""
    global passed, failed
    matches = [e for e in errors if expected_fragment in e]
    if matches:
        print(f"  ✓  {label}")
        passed += 1
    else:
        print(f"  ✗  {label}")
        print(f"       Expected fragment: '{expected_fragment}'")
        print(f"       Actual errors: {errors if errors else '(none)'}")
        failed += 1

def expect_no_errors(label, errors):
    """Assert that the error list is empty."""
    global passed, failed
    if not errors:
        print(f"  ✓  {label}")
        passed += 1
    else:
        print(f"  ✗  {label}")
        print(f"       Expected no errors, got: {errors}")
        failed += 1

def expect_warnings(label, warnings, expected_fragment):
    global passed, failed
    matches = [w for w in warnings if expected_fragment in w]
    if matches:
        print(f"  ✓  {label}")
        passed += 1
    else:
        print(f"  ✗  {label}")
        print(f"       Expected fragment: '{expected_fragment}'")
        print(f"       Actual warnings: {warnings if warnings else '(none)'}")
        failed += 1


# ── Good base fixtures ────────────────────────────────────────────────────────

GOOD_COLUMNS = [
    {"key": "name",        "label": "Document name", "required": True,  "type": "text"},
    {"key": "status",      "label": "Status",        "required": True,  "type": "text"},
    {"key": "change_date", "label": "Change date",   "required": True,  "type": "date"},
    {"key": "version",     "label": "Version",       "required": False, "type": "version"},
]

GOOD_FILES = [
    {"filename": "report.pdf",  "name": "Report",  "status": "Approved",   "change_date": "2025-01-15", "version": "1.0"},
    {"filename": "drawing.dwg", "name": "Drawing", "status": "Draft",      "change_date": "2025-03-01", "version": "0.2"},
]


# ── Tests: schema structure ───────────────────────────────────────────────────

print("\nschema structure")

expect_no_errors(
    "valid schema passes cleanly",
    v.check_schema_structure(GOOD_COLUMNS)
)

expect_errors(
    "schema entry missing 'key' is caught",
    v.check_schema_structure([{"label": "X", "required": True, "type": "text"}]),
    "missing field 'key'"
)

expect_errors(
    "schema entry missing 'type' is caught",
    v.check_schema_structure([{"key": "x", "label": "X", "required": True}]),
    "missing field 'type'"
)

expect_errors(
    "invalid type value is caught",
    v.check_schema_structure([{"key": "x", "label": "X", "required": True, "type": "number"}]),
    "must be one of"
)

expect_errors(
    "'required' must be bool not string",
    v.check_schema_structure([{"key": "x", "label": "X", "required": "yes", "type": "text"}]),
    "'required' must be True or False"
)


# ── Tests: schema duplicate keys ─────────────────────────────────────────────

print("\nschema duplicate keys")

expect_no_errors(
    "unique keys pass",
    v.check_schema_no_duplicate_keys(GOOD_COLUMNS)
)

expect_errors(
    "duplicate key is caught",
    v.check_schema_no_duplicate_keys([
        {"key": "name", "label": "A", "required": True, "type": "text"},
        {"key": "name", "label": "B", "required": True, "type": "text"},
    ]),
    "duplicate key 'name'"
)


# ── Tests: metadata filename ──────────────────────────────────────────────────

print("\nmetadata filename")

expect_no_errors(
    "valid filenames pass",
    v.check_metadata_has_filename(GOOD_FILES)
)

expect_errors(
    "missing filename is caught",
    v.check_metadata_has_filename([{"name": "X", "status": "Draft"}]),
    "missing 'filename'"
)

expect_errors(
    "empty filename string is caught",
    v.check_metadata_has_filename([{"filename": "   "}]),
    "non-empty string"
)


# ── Tests: duplicate filenames ────────────────────────────────────────────────

print("\nduplicate filenames")

expect_no_errors(
    "unique filenames pass",
    v.check_metadata_no_duplicate_filenames(GOOD_FILES)
)

expect_errors(
    "duplicate filename is caught",
    v.check_metadata_no_duplicate_filenames([
        {"filename": "a.pdf"},
        {"filename": "a.pdf"},
    ]),
    "duplicate filename 'a.pdf'"
)


# ── Tests: required fields ────────────────────────────────────────────────────

print("\nrequired fields")

expect_no_errors(
    "all required fields present passes",
    v.check_required_fields_present(GOOD_FILES, GOOD_COLUMNS)
)

expect_errors(
    "missing required field is caught",
    v.check_required_fields_present(
        [{"filename": "x.pdf", "name": "X", "change_date": "2025-01-01"}],
        GOOD_COLUMNS
    ),
    "missing required field 'status'"
)


# ── Tests: extra keys ─────────────────────────────────────────────────────────

print("\nextra keys")

expect_no_errors(
    "no extra keys → no warnings",
    v.check_no_extra_keys(GOOD_FILES, GOOD_COLUMNS)
)

expect_warnings(
    "extra key produces a warning",
    v.check_no_extra_keys(
        [{"filename": "x.pdf", "name": "X", "status": "Draft",
          "change_date": "2025-01-01", "mystery_field": "???"}],
        GOOD_COLUMNS
    ),
    "mystery_field"
)


# ── Tests: date format ────────────────────────────────────────────────────────

print("\ndate format")

expect_no_errors(
    "valid date passes",
    v.check_date_format(GOOD_FILES, GOOD_COLUMNS)
)

expect_errors(
    "wrong date format is caught",
    v.check_date_format(
        [{"filename": "x.pdf", "change_date": "15-01-2025"}],
        GOOD_COLUMNS
    ),
    "not a valid date"
)

expect_errors(
    "non-date string is caught",
    v.check_date_format(
        [{"filename": "x.pdf", "change_date": "January 2025"}],
        GOOD_COLUMNS
    ),
    "not a valid date"
)


# ── Tests: files exist in input/ ─────────────────────────────────────────────

print("\nfiles exist in input/")

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    (tmp / "present.pdf").write_bytes(b"%PDF-1.4")

    expect_no_errors(
        "existing file passes",
        v.check_files_exist_in_input([{"filename": "present.pdf"}], tmp)
    )

    expect_errors(
        "missing file is caught",
        v.check_files_exist_in_input([{"filename": "ghost.pdf"}], tmp),
        "not found in"
    )


# ── Tests: orphan files in input/ ────────────────────────────────────────────

print("\norphan files in input/")

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    (tmp / "orphan.pdf").write_bytes(b"%PDF-1.4")

    expect_warnings(
        "file in input/ with no metadata entry produces warning",
        v.check_all_input_files_have_metadata([], tmp),
        "orphan.pdf"
    )

    expect_no_errors(
        "declared file does not produce orphan warning",
        v.check_all_input_files_have_metadata([{"filename": "orphan.pdf"}], tmp)
    )


# ── Summary ───────────────────────────────────────────────────────────────────

total = passed + failed
print(f"\n{'─'*50}")
print(f"  {passed}/{total} tests passed", end="")
if failed:
    print(f"  —  {failed} FAILED")
    sys.exit(1)
else:
    print("  —  all good.")
    sys.exit(0)
