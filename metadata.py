# metadata.py
# ─────────────────────────────────────────────────────────────────────────────
# ONE ENTRY PER FILE in the bundle.
#
# Rules:
#   - "filename" must match the exact file name inside the input/ folder
#   - All keys defined as required in schema.py must be present in every entry
#   - Extra keys not in schema.py are allowed but will be ignored by the packer
#   - Date format for "change_date": YYYY-MM-DD
# ─────────────────────────────────────────────────────────────────────────────

FILES = [
    {
        "filename":    "README_FA_ABZ.pdf",
        "name":        "README_FA_ABZ",
        "status":      "Approved",
        "change_date": "2025-04-15",
        "version":     "2.1",
    },
    {
        "filename":    "OSS_XXXXXXX-SEMCO-Z-TB-0001_Division of Responsibility (DoR) (4).xlsx",
        "name":        "OSS_XXXXXXX-SEMCO-Z-TB-0001_Division of Responsibility (DoR) (4)",
        "status":      "Approved",
        "change_date": "2025-04-15",
        "version":     "1.3",
    },
    {
        "filename":    "OSS_XXXXXXX-SEMCO-B-FD-0001_Systems Technical Description (30).docx",
        "name":        "OSS_XXXXXXX-SEMCO-B-FD-0001_Systems Technical Description (30)",
        "status":      "Draft",
        "change_date": "2025-04-28",
        "version":     "0.4",
    },
    {
        "filename":    "L1.LC8_XXXXXXX-SEMCO-I-XI-0008_Block Diagram - Auxiliary Control and Monitoring System (ACMS) (1).vsdm",
        "name":        "L1.LC8_XXXXXXX-SEMCO-I-XI-0008_Block Diagram - Auxiliary Control and Monitoring System (ACMS) (1)",
        "status":      "Draft",
        "change_date": "2025-04-28",
        "version":     "0.4",
    },
    {
        "filename":    "ABZ-HO1437-S3A-002.R00 (3).pdf",
        "name":        "ABZ-HO1437-S3A-002.R00 (3)",
        "status":      "For review",
        "change_date": "2025-03-10",
        "version":     "1.0",
    },
]
