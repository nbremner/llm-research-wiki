#!/usr/bin/env python3
# /// script
# dependencies = ["numbers-parser"]
# ///
"""Extract a reviewed Apple Numbers triage workbook to CSV and summarize reviewed rows.

Run:
  uv run /root/research-wiki-tools/numbers_review_extract.py input.numbers --out output.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from numbers_parser import Document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers_path")
    parser.add_argument("--out", default=None)
    parser.add_argument("--summary-json", default=None)
    args = parser.parse_args()

    numbers_path = Path(args.numbers_path).resolve()
    out = Path(args.out).resolve() if args.out else numbers_path.with_suffix(".csv")
    summary_json = Path(args.summary_json).resolve() if args.summary_json else out.with_suffix(".review_summary.json")

    doc = Document(str(numbers_path))
    if not doc.sheets or not doc.sheets[0].tables:
        raise SystemExit("No sheets/tables found in Numbers file")
    table = doc.sheets[0].tables[0]
    headers = [table.cell(0, c).value for c in range(table.num_cols)]
    rows = []
    reviewed = []
    for r in range(1, table.num_rows):
        row = {headers[c]: table.cell(r, c).value for c in range(table.num_cols)}
        rows.append(row)
        status = str(row.get("human_review_status") or "").strip()
        notes = str(row.get("human_review_notes") or "").strip()
        if status or notes:
            reviewed.append(row)

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "numbers_path": str(numbers_path),
        "csv_path": str(out),
        "sheet_count": len(doc.sheets),
        "table_name": table.name,
        "row_count": len(rows),
        "column_count": len(headers),
        "reviewed_count": len(reviewed),
        "reviewed": [
            {
                "filename": r.get("original_filename"),
                "status": r.get("human_review_status"),
                "notes": r.get("human_review_notes"),
                "flags": r.get("boundary_flags"),
                "detected_title": r.get("detected_title"),
                "topics": r.get("suggested_topics"),
                "doi": r.get("doi"),
            }
            for r in reviewed
        ],
    }
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
