# validate.py
# ─────────────────────────────────────────────────────────────────────────────
# Validation logic. Called automatically by pack_bundle.py on every run.
#
# This file is not meant to be run directly in normal workflow.
# It is imported by pack_bundle.py and by test_validate.py.
# ─────────────────────────────────────────────────────────────────────────────

import re
from pathlib import Path


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ── Individual check functions ────────────────────────────────────────────────
# Each function receives the full data and returns a list of error strings.
# Empty list = no errors found.

def check_schema_structure(columns):
    """Schema entries must each have key, label, required, type."""
    errors = []
    allowed_types = {"text", "date", "version"}
    for i, col in enumerate(columns):
        prefix = f"schema.py column [{i}]"
        for field in ("key", "label", "required", "type"):
            if field not in col:
                errors.append(f"{prefix}: missing field '{field}'")
        if "key" in col and not isinstance(col["key"], str):
            errors.append(f"{prefix}: 'key' must be a string")
        if "label" in col and not isinstance(col["label"], str):
            errors.append(f"{prefix}: 'label' must be a string")
        if "required" in col and not isinstance(col["required"], bool):
            errors.append(f"{prefix}: 'required' must be True or False")
        if "type" in col and col["type"] not in allowed_types:
            errors.append(
                f"{prefix}: 'type' is '{col['type']}', must be one of {sorted(allowed_types)}"
            )
    return errors


def check_schema_no_duplicate_keys(columns):
    """All column keys in schema must be unique."""
    errors = []
    seen = {}
    for i, col in enumerate(columns):
        key = col.get("key")
        if key is None:
            continue
        if key in seen:
            errors.append(
                f"schema.py: duplicate key '{key}' at columns [{seen[key]}] and [{i}]"
            )
        else:
            seen[key] = i
    return errors


def check_metadata_has_filename(files):
    """Every metadata entry must have a non-empty 'filename'."""
    errors = []
    for i, entry in enumerate(files):
        if "filename" not in entry:
            errors.append(f"metadata.py entry [{i}]: missing 'filename'")
        elif not isinstance(entry["filename"], str) or not entry["filename"].strip():
            errors.append(f"metadata.py entry [{i}]: 'filename' must be a non-empty string")
    return errors


def check_metadata_no_duplicate_filenames(files):
    """Each filename must appear only once in metadata."""
    errors = []
    seen = {}
    for i, entry in enumerate(files):
        fn = entry.get("filename")
        if fn is None:
            continue
        if fn in seen:
            errors.append(
                f"metadata.py: duplicate filename '{fn}' at entries [{seen[fn]}] and [{i}]"
            )
        else:
            seen[fn] = i
    return errors


def check_required_fields_present(files, columns):
    """Every required column key must exist in every metadata entry."""
    errors = []
    required_keys = [c["key"] for c in columns if c.get("required")]
    for i, entry in enumerate(files):
        fn = entry.get("filename", f"entry [{i}]")
        for key in required_keys:
            if key not in entry:
                errors.append(
                    f"metadata.py '{fn}': missing required field '{key}'"
                )
    return errors


def check_no_extra_keys(files, columns):
    """Warn (not error) if an entry has keys not defined in schema."""
    warnings = []
    known_keys = {c["key"] for c in columns} | {"filename"}
    for i, entry in enumerate(files):
        fn = entry.get("filename", f"entry [{i}]")
        for key in entry:
            if key not in known_keys:
                warnings.append(
                    f"metadata.py '{fn}': key '{key}' is not in schema.py (will be ignored)"
                )
    return warnings


def check_date_format(files, columns):
    """Fields with type='date' must follow YYYY-MM-DD format."""
    errors = []
    date_keys = [c["key"] for c in columns if c.get("type") == "date"]
    for entry in files:
        fn = entry.get("filename", "?")
        for key in date_keys:
            value = entry.get(key)
            if value is None:
                continue  # already caught by required check
            if not isinstance(value, str) or not DATE_PATTERN.match(value):
                errors.append(
                    f"metadata.py '{fn}': field '{key}' value '{value}' "
                    f"is not a valid date — expected YYYY-MM-DD"
                )
    return errors


def check_files_exist_in_input(files, input_dir: Path):
    """Every filename in metadata must exist as a file inside input/."""
    errors = []
    for entry in files:
        fn = entry.get("filename")
        if not fn:
            continue
        if not (input_dir / fn).is_file():
            errors.append(
                f"metadata.py '{fn}': file not found in '{input_dir}/'"
            )
    return errors


def check_all_input_files_have_metadata(files, input_dir: Path):
    """Warn if a file exists in input/ but has no metadata entry."""
    warnings = []
    declared = {entry.get("filename") for entry in files}
    for fp in sorted(input_dir.iterdir()):
        if fp.is_file() and fp.name not in declared:
            warnings.append(
                f"input/{fp.name}: file exists but has no entry in metadata.py"
            )
    return warnings


# ── Main validation runner ────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    @property
    def ok(self):
        return len(self.errors) == 0

    def add_errors(self, lst):
        self.errors.extend(lst)

    def add_warnings(self, lst):
        self.warnings.extend(lst)


def run_all_checks(columns, files, input_dir: Path) -> ValidationResult:
    result = ValidationResult()

    result.add_errors(check_schema_structure(columns))
    result.add_errors(check_schema_no_duplicate_keys(columns))
    result.add_errors(check_metadata_has_filename(files))
    result.add_errors(check_metadata_no_duplicate_filenames(files))
    result.add_errors(check_required_fields_present(files, columns))
    result.add_errors(check_date_format(files, columns))
    result.add_errors(check_files_exist_in_input(files, input_dir))
    result.add_warnings(check_no_extra_keys(files, columns))
    result.add_warnings(check_all_input_files_have_metadata(files, input_dir))

    return result


def print_report(result: ValidationResult):
    if result.errors:
        print(f"\n  ERRORS ({len(result.errors)} found):")
        for e in result.errors:
            print(f"    ✗  {e}")
    if result.warnings:
        print(f"\n  WARNINGS ({len(result.warnings)} found):")
        for w in result.warnings:
            print(f"    ⚠  {w}")
    if result.ok and not result.warnings:
        print("    ✓  All checks passed.")
    elif result.ok:
        print(f"\n    ✓  No errors. {len(result.warnings)} warning(s) above (bundle will still be built).")
