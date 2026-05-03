# pack_bundle.py
# ─────────────────────────────────────────────────────────────────────────────
# Main script. Run this to validate and build the HTML bundle.
#
# Usage:
#   python pack_bundle.py
#   python pack_bundle.py --title "Framework Agreement Q2-2025"
#   python pack_bundle.py --output my_bundle.html
#
# What it does:
#   1. Imports schema.py and metadata.py
#   2. Runs all validation checks — stops with a clear error report if anything
#      is wrong
#   3. Reads each file from input/
#   4. Builds a single self-contained HTML file in output/
# ─────────────────────────────────────────────────────────────────────────────

import argparse
import base64
from datetime import datetime
import mimetypes
import sys
from pathlib import Path

import validate
from schema import COLUMNS
from metadata import FILES

INPUT_DIR  = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"

EXTRA_MIME = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".pdf":  "application/pdf",
    ".msg":  "application/vnd.ms-outlook",
    ".dwg":  "image/vnd.dwg",
    ".vsdx": "application/vnd.ms-visio.drawing",
    ".vsdm": "application/vnd.ms-visio.drawing.macroEnabled",
    ".vsd":  "application/vnd.visio",
}

def get_mime(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in EXTRA_MIME:
        return EXTRA_MIME[ext]
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


# ── Step 1: Validation ────────────────────────────────────────────────────────

def run_validation():
    print("\n[ 1/3 ] Validating schema and metadata...")
    result = validate.run_all_checks(COLUMNS, FILES, INPUT_DIR)
    validate.print_report(result)
    if not result.ok:
        print("\n  Bundle was NOT built. Fix the errors above and run again.\n")
        sys.exit(1)
    return result


# ── Step 2: Build file records ────────────────────────────────────────────────

def build_file_records() -> list:
    print("\n[ 2/3 ] Reading files from input/...")
    records = []
    for entry in FILES:
        fn = entry["filename"]
        fp = INPUT_DIR / fn
        raw  = fp.read_bytes()
        b64  = base64.b64encode(raw).decode("ascii")
        size = fp.stat().st_size
        record = {
            "filename": fn,
            "mime":     get_mime(fn),
            "size":     size,
            "b64":      b64,
        }
        # attach schema-defined metadata fields
        for col in COLUMNS:
            record[col["key"]] = entry.get(col["key"], "")
        records.append(record)
        print(f"    + {fn}  ({size/1024:.1f} KB)")
    return records


# ── Step 3: Render HTML ───────────────────────────────────────────────────────

def human_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n/1024:.1f} KB"
    return f"{n/1024/1024:.1f} MB"


def render_html(title: str, records: list) -> str:
    from datetime import datetime
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Column header cells ──
    header_cells = "\n".join(
        f'          <th>{col["label"]}</th>' for col in COLUMNS
    )

    # ── One <tr> per file ──
    rows_html = []
    for rec in records:
        cells = []
        for col in COLUMNS:
            val = rec.get(col["key"], "")
            cells.append(f"          <td>{val}</td>")
        # download cell: inline base64 blob → browser save dialog
        cells.append(
            f'          <td><button class="dl-btn" '
            f'data-b64="{rec["b64"]}" '
            f'data-mime="{rec["mime"]}" '
            f'data-filename="{rec["filename"]}">'
            f'Download</button></td>'
        )
        rows_html.append("        <tr>\n" + "\n".join(cells) + "\n        </tr>")

    rows = "\n".join(rows_html)
    file_count = len(records)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg:      #f8f7f4;
  --surface: #ffffff;
  --border:  #d4d3cf;
  --text:    #1a1a18;
  --text2:   #5a5a57;
  --text3:   #8a8a87;
  --accent:  #534AB7;
  --accent-h:#3e3490;
  --radius:  6px;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg:      #1c1c1a;
    --surface: #242422;
    --border:  #3c3c38;
    --text:    #e8e7e2;
    --text2:   #a8a8a4;
    --text3:   #6a6a66;
    --accent:  #AFA9EC;
    --accent-h:#cbc7f5;
  }}
}}
body {{
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 14px;
  background: var(--bg);
  color: var(--text);
  padding: 40px 32px;
  line-height: 1.5;
}}
header {{
  margin-bottom: 28px;
}}
header h1 {{
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}}
header p {{
  font-size: 13px;
  color: var(--text3);
}}
table {{
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}}
thead th {{
  text-align: left;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text3);
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}}
tbody tr {{
  border-bottom: 1px solid var(--border);
}}
tbody tr:last-child {{
  border-bottom: none;
}}
tbody tr:hover {{
  background: var(--bg);
}}
td {{
  padding: 10px 14px;
  font-size: 13px;
  color: var(--text);
  vertical-align: middle;
}}
td:last-child {{
  width: 1%;
  white-space: nowrap;
}}
.dl-btn {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}}
.dl-btn:hover {{
  background: var(--accent-h);
}}
footer {{
  margin-top: 20px;
  font-size: 12px;
  color: var(--text3);
}}
</style>
</head>
<body>

<header>
  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px;">
    <div>
      <h1>{title}</h1>
      <p>{file_count} file{"s" if file_count != 1 else ""} bundled</p>
    </div>
    <button class="dl-btn" id="dl-all-btn" style="margin-top:4px; white-space:nowrap;">
      Download all
    </button>
  </div>
</header>

<table>
  <thead>
    <tr>
{header_cells}
      <th></th>
    </tr>
  </thead>
  <tbody>
{rows}
  </tbody>
</table>

<footer>
  Generated on {generated_on} &nbsp;·&nbsp; Open in any modern browser &nbsp;·&nbsp; No internet connection required
</footer>

<footer style="margin-top:8px; font-size:12px; color:var(--text3); border-top:1px solid var(--border); padding-top:10px;">
  Docs_Packer © 2026 IPOLIPOL.
</footer>

<script>
document.getElementById("dl-all-btn").addEventListener("click", function() {{
  document.querySelectorAll(".dl-btn[data-filename]").forEach(function(btn) {{
    btn.click();
  }});
}});
document.querySelectorAll(".dl-btn").forEach(function(btn) {{
  btn.addEventListener("click", function() {{
    var b64      = btn.dataset.b64;
    var mime     = btn.dataset.mime;
    var filename = btn.dataset.filename;
    var binStr   = atob(b64);
    var bytes    = new Uint8Array(binStr.length);
    for (var i = 0; i < binStr.length; i++) {{
      bytes[i] = binStr.charCodeAt(i);
    }}
    var blob = new Blob([bytes], {{ type: mime }});
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement("a");
    a.href     = url;
    a.download = filename;
    a.click();
    setTimeout(function() {{ URL.revokeObjectURL(url); }}, 5000);
  }});
}});
</script>

</body>
</html>"""


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build a portable HTML bundle.")
    parser.add_argument("--title",  default="Document bundle", help="Title shown in the HTML page")
    parser.add_argument("--output", default="",                help="Output filename (default: <title>.html)")
    args = parser.parse_args()

    title = args.title
    out_name = args.output or (title.replace(" ", "_") + ".html")
    out_path = OUTPUT_DIR / out_name

    print(f"\n  pack_bundle.py")
    print(f"  Title  : {title}")
    print(f"  Input  : {INPUT_DIR}")
    print(f"  Output : {out_path}")

    # Step 1
    run_validation()

    # Step 2
    records = build_file_records()

    # Step 3
    print(f"\n[ 3/3 ] Building HTML...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    html = render_html(title, records)
    out_path.write_text(html, encoding="utf-8")

    size_kb = out_path.stat().st_size / 1024
    print(f"    → {out_path}  ({size_kb:.1f} KB)")
    print(f"\n  Done. Open the HTML file in any browser.\n")


if __name__ == "__main__":
    main()
