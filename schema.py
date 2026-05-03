# schema.py
# ─────────────────────────────────────────────────────────────────────────────
# THIS FILE IS THE SINGLE SOURCE OF TRUTH FOR THE TABLE STRUCTURE.
#
# Each column is a dict with these fields:
#
#   key      (str, required) — internal identifier, must match keys in metadata.py
#   label    (str, required) — column header shown in the HTML table
#   required (bool)          — if True, every file entry must have this key
#   type     (str)           — "text" | "date" | "version"
#                              used for display formatting in the HTML table
#
# Rules:
#   - "filename" is always required and always the first column implicitly —
#     do not add it here, it is handled automatically by the packer
#   - Order of entries here = order of columns in the HTML table
#   - To add a column: add an entry here, then add the key to every entry
#     in metadata.py, then re-run pack_bundle.py
# ─────────────────────────────────────────────────────────────────────────────

COLUMNS = [
    {
        "key":      "name",
        "label":    "Document name",
        "required": True,
        "type":     "text",
    },
    {
        "key":      "status",
        "label":    "Status",
        "required": True,
        "type":     "text",
    },
    {
        "key":      "change_date",
        "label":    "Change date",
        "required": True,
        "type":     "date",
    },
    {
        "key":      "version",
        "label":    "Version",
        "required": True,
        "type":     "version",
    },
]
