"""
Ingest EAPCET cutoff ranks from docs/tables/ PDFs into Firestore.

Handles 2023, 2024, 2025 PDFs.
- Skips records already in Firestore that already have first_rank (no true duplicates)
- Uses upsert (merge=True) to patch records that exist but lack first_rank
- Supports --dry-run, --year filter, --pdf

Usage:
    python ingest_tables_pdfs.py --dry-run
    python ingest_tables_pdfs.py --year 2024 --dry-run
    python ingest_tables_pdfs.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Year -> PDF file mapping
# ---------------------------------------------------------------------------
TABLES_DIR = Path("docs/tables")

PDF_MAP = {
    2025: "2025-TGEAPCET-Cutoff-Ranks.pdf",
    2024: "EAPCET_First-and-Last-Ranks-2024.pdf",
    2023: "First-and-Last-Ranks-2023-Eamcet.pdf",
    # 2022 PDF is image-based; pdfplumber cannot extract tables from it
}


# ---------------------------------------------------------------------------
# Column layouts for regular pages (First/Last per gender per category)
# Format: (category, gender, first_col_index, last_col_index)
# ---------------------------------------------------------------------------

def _regular_cols(categories: list[str]) -> list[tuple]:
    """
    Build (category, gender, first_col, last_col) tuples for a regular table.

    Layout: Branch | Cat1_BF | Cat1_BL | Cat1_GF | Cat1_GL | Cat2_BF | ...
    Where BF=Boys-First, BL=Boys-Last, GF=Girls-First, GL=Girls-Last
    """
    entries = []
    for i, cat in enumerate(categories):
        base = i * 4 + 1
        entries.append((cat, "Boys",  base,     base + 1))
        entries.append((cat, "Girls", base + 2, base + 3))
    return entries


PAGE1_CATEGORIES  = ["OC", "BC-A", "BC-B", "BC-C"]
PAGE2_2025_CATS   = ["BC-D", "BC-E", "SC-I", "SC-II", "SC-III", "ST"]
PAGE2_2023_CATS   = ["BC-D", "BC-E", "SC", "ST"]       # 2023 and 2024
PAGE3_SPECIAL_CATS = ["SPORTS", "CAP", "NCC", "OTHERS"]  # First/Last format

# EWS page column positions
EWS_2025_COLS  = {"boys_first": 1, "boys_last": 2, "girls_first": 3, "girls_last": 4}
EWS_2023_COLS  = {"boys_first": 3, "boys_last": 8, "girls_first": 9, "girls_last": 15}
EWS_2024_COLS  = {"boys_first": 3, "boys_last": 8, "girls_first": 9, "girls_last": 16}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_rank(value) -> int | None:
    """Parse a rank value  ('-', '--', None, '1234') -> int or None."""
    if value is None:
        return None
    v = str(value).strip()
    if not v or v in ("-", "--", "—"):
        return None
    # Strip commas/spaces
    v = re.sub(r"[,\s]", "", v)
    v = re.sub(r"\.0+$", "", v)
    m = re.match(r"^(\d+)$", v)
    return int(m.group(1)) if m else None


def normalize_branch(raw: str) -> str:
    """Normalize branch name  (strip extra spaces, newlines etc.)."""
    b = str(raw).strip()
    b = re.sub(r"\s*\n\s*", "", b)       # remove embedded newlines
    b = re.sub(r"-\s+", "-", b)          # "CSE- CSC" -> "CSE-CSC"
    b = re.sub(r"\s+", " ", b).strip()   # collapse multiple spaces
    return b


def _doc_id(rec: dict) -> str:
    base = (
        f"{rec['branch']}_{rec['category']}_{rec['year']}_"
        f"R{rec['round']}_{rec['gender']}_{rec['quota']}"
    )
    if rec.get("ph_type"):
        base += f"_{rec['ph_type']}"
    return base.replace(" ", "-").replace("(", "").replace(")", "")


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _data_rows(table: list[list], n_header_rows: int = 3) -> list[list]:
    """Return rows after the header block, skipping rows with empty branch."""
    rows = []
    for row in table[n_header_rows:]:
        if not row:
            continue
        branch_raw = str(row[0]).strip() if row[0] else ""
        if not branch_raw:
            continue
        rows.append(row)
    return rows


def extract_regular_table(
    table: list[list],
    categories: list[str],
    year: int,
    quota: str = "Convenor",
) -> list[dict]:
    """
    Extract records from a standard First/Last table.
    3 header rows then branch data rows.
    """
    col_map = _regular_cols(categories)
    records: list[dict] = []

    for row in _data_rows(table):
        branch = normalize_branch(str(row[0]) if row[0] else "")
        if not branch or branch.lower() in ("branch", ""):
            continue

        for cat, gender, first_col, last_col in col_map:
            if last_col >= len(row):
                continue
            first_rank = parse_rank(row[first_col])
            last_rank  = parse_rank(row[last_col])

            if last_rank is None and first_rank is None:
                continue
            # If only one value, treat as Last rank
            if last_rank is None:
                last_rank = first_rank

            rec: dict = {
                "branch":      branch,
                "category":    cat,
                "gender":      gender,
                "year":        year,
                "round":       1,
                "quota":       quota,
                "cutoff_rank": last_rank,
                "last_rank":   last_rank,
            }
            if first_rank is not None:
                rec["first_rank"] = first_rank
            records.append(rec)

    return records


def extract_ews_table(
    table: list[list],
    year: int,
    col_positions: dict,
) -> list[dict]:
    """
    Extract EWS records from the EWS page (different column layouts per year).
    col_positions: dict with boys_first, boys_last, girls_first, girls_last
    """
    records: list[dict] = []
    bf = col_positions["boys_first"]
    bl = col_positions["boys_last"]
    gf = col_positions["girls_first"]
    gl = col_positions["girls_last"]

    for row in _data_rows(table):
        branch = normalize_branch(str(row[0]) if row[0] else "")
        if not branch:
            continue

        for gender, first_col, last_col in [("Boys", bf, bl), ("Girls", gf, gl)]:
            if last_col >= len(row):
                continue
            first_rank = parse_rank(row[first_col])
            last_rank  = parse_rank(row[last_col])
            if last_rank is None and first_rank is None:
                continue
            if last_rank is None:
                last_rank = first_rank
            rec: dict = {
                "branch":      branch,
                "category":    "EWS",
                "gender":      gender,
                "year":        year,
                "round":       1,
                "quota":       "Convenor",
                "cutoff_rank": last_rank,
                "last_rank":   last_rank,
            }
            if first_rank is not None:
                rec["first_rank"] = first_rank
            records.append(rec)

    return records


# ---------------------------------------------------------------------------
# Per-PDF extraction
# ---------------------------------------------------------------------------

def extract_pdf(pdf_path: Path, year: int) -> list[dict]:
    """Extract all records from a cutoff PDF."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Run: pip install pdfplumber")

    all_records: list[dict] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        n_pages = len(pdf.pages)
        print(f"  [PDF] {pdf_path.name}  ({n_pages} pages)")

        # Helper: get largest table from a page
        def get_table(pg_idx: int) -> list[list] | None:
            if pg_idx >= n_pages:
                return None
            tbls = pdf.pages[pg_idx].extract_tables()
            if not tbls:
                return None
            return max(tbls, key=lambda t: len(t) if t else 0)

        # ── Page 1 (0-indexed 0): OC, BC-A, BC-B, BC-C ──
        t = get_table(0)
        if t:
            recs = extract_regular_table(t, PAGE1_CATEGORIES, year)
            print(f"    Page 1: {len(recs)} records  (OC/BC-A/BC-B/BC-C)")
            all_records.extend(recs)

        # ── Page 2 (0-indexed 1): BC-D, BC-E, SC*, ST ──
        t = get_table(1)
        if t:
            # Detect layout by column count
            n_cols = len(t[0]) if t[0] else 0
            cats = PAGE2_2025_CATS if n_cols >= 24 else PAGE2_2023_CATS
            recs = extract_regular_table(t, cats, year)
            print(f"    Page 2: {len(recs)} records  ({', '.join(cats)})  [{n_cols} cols]")
            all_records.extend(recs)

        if year == 2025:
            # ── Page 3 (special categories) and Page 4 (special alt) ──
            # Page 3 (0-indexed 2): SPORTS, CAP, NCC, OTHERS — First/Last format
            t = get_table(2)
            if t:
                recs = extract_regular_table(t, PAGE3_SPECIAL_CATS, year)
                print(f"    Page 3: {len(recs)} records  (SPORTS/CAP/NCC/OTHERS)")
                all_records.extend(recs)

            # ── Page 5 (0-indexed 4): EWS — clean 5-col layout ──
            t = get_table(4)
            if t:
                recs = extract_ews_table(t, year, EWS_2025_COLS)
                print(f"    Page 5: {len(recs)} records  (EWS)")
                all_records.extend(recs)
        else:
            # 2023 / 2024: Page 3 = special (skip combined format cells)
            t = get_table(2)
            if t:
                n_cols = len(t[0]) if t[0] else 0
                # Check if rows have numeric-only data (First/Last format)
                # by testing a sample data cell
                sample_rows = _data_rows(t)
                if sample_rows:
                    sample_cell = str(sample_rows[0][1]).strip() if len(sample_rows[0]) > 1 else ""
                    if re.match(r"^\d+$", sample_cell):
                        recs = extract_regular_table(t, PAGE3_SPECIAL_CATS, year)
                        print(f"    Page 3: {len(recs)} records  (SPORTS/CAP/NCC/OTHERS)")
                        all_records.extend(recs)
                    else:
                        print(f"    Page 3: skipped (combined rank-category format not numeric)")

            # ── Page 4 (0-indexed 3): EWS ──
            t = get_table(3)
            if t:
                n_cols = len(t[0]) if t[0] else 0
                col_pos = EWS_2024_COLS if n_cols >= 19 else EWS_2023_COLS
                recs = extract_ews_table(t, year, col_pos)
                print(f"    Page 4: {len(recs)} records  (EWS)  [{n_cols} cols]")
                all_records.extend(recs)

    return all_records


# ---------------------------------------------------------------------------
# Firestore upsert (with duplicate skip)
# ---------------------------------------------------------------------------

def get_existing_doc_ids(db, year: int) -> dict[str, bool]:
    """
    Fetch all doc IDs for given year.
    Returns {doc_id: has_first_rank}
    """
    result: dict[str, bool] = {}
    try:
        from google.cloud.firestore_v1.base_query import FieldFilter
        docs = (
            db.collection(COLLECTION)
            .where(filter=FieldFilter("year", "==", year))
            .stream()
        )
        for doc in docs:
            d = doc.to_dict()
            result[doc.id] = d.get("first_rank") is not None
    except Exception as e:
        print(f"[WARN] Could not prefetch existing IDs for {year}: {e}")
    return result


def upload_records(
    records: list[dict],
    existing: dict[str, bool],
    dry_run: bool,
    db,
) -> tuple[int, int, int]:
    """
    Upload records avoiding real duplicates.
    - If doc exists AND has first_rank: SKIP (already complete)
    - If doc exists but lacks first_rank: UPDATE (merge=True)
    - If doc does not exist: INSERT

    Returns (inserted, updated, skipped)
    """
    inserted = updated = skipped = 0
    batch = db.batch()
    batch_count = 0

    for rec in records:
        doc_id = _doc_id(rec)
        has_fr = existing.get(doc_id)

        if doc_id in existing and has_fr:
            # Complete record exists — skip
            skipped += 1
            continue

        action = "UPDATE" if doc_id in existing else "INSERT"
        if action == "UPDATE":
            updated += 1
        else:
            inserted += 1

        if dry_run:
            fr = rec.get("first_rank", "N/A")
            lr = rec.get("last_rank", rec.get("cutoff_rank", "N/A"))
            print(
                f"  [{action:6s}] {doc_id:<55s} "
                f"first={str(fr):>7s}  last={str(lr):>7s}"
            )
        else:
            ref = db.collection(COLLECTION).document(doc_id)
            batch.set(ref, rec, merge=True)
            batch_count += 1
            if batch_count % 400 == 0:
                batch.commit()
                batch = db.batch()
                print(f"  ... committed {batch_count} writes ...")

    if not dry_run and batch_count > 0:
        batch.commit()

    return inserted, updated, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ingest cutoff PDFs from docs/tables/ into Firestore")
    parser.add_argument("--year", type=int, default=None, help="Only process this year (2023/2024/2025)")
    parser.add_argument("--pdf", type=str, default=None, help="Path to a specific PDF (overrides auto-lookup)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to Firestore")
    args = parser.parse_args()

    years_to_process = [args.year] if args.year else sorted(PDF_MAP.keys())

    from app.data.init_db import get_db, COLLECTION as _COLLECTION  # noqa: F401
    global COLLECTION
    COLLECTION = _COLLECTION

    db = get_db()
    if db is None and not args.dry_run:
        print("[ERROR] Firestore not available.")
        sys.exit(1)

    total_inserted = total_updated = total_skipped = 0

    for year in years_to_process:
        if args.pdf:
            pdf_path = Path(args.pdf)
        else:
            pdf_name = PDF_MAP.get(year)
            if not pdf_name:
                print(f"\n[SKIP] No PDF mapping for year {year}")
                continue
            pdf_path = TABLES_DIR / pdf_name

        if not pdf_path.exists():
            print(f"\n[SKIP] PDF not found: {pdf_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Year {year}")

        # Extract records from PDF
        records = extract_pdf(pdf_path, year)
        fr_count = sum(1 for r in records if r.get("first_rank") is not None)
        print(f"  Extracted {len(records)} records  ({fr_count} with first_rank)")

        if not records:
            print("  No records extracted; skipping.")
            continue

        # Pre-fetch existing Firestore doc IDs for this year
        if args.dry_run and db is None:
            existing: dict[str, bool] = {}
            print("  [DRY-RUN] Skipping Firestore prefetch (no db connection).")
        else:
            print(f"  Prefetching existing Firestore docs for year {year} ...")
            existing = get_existing_doc_ids(db, year)
            print(f"  Found {len(existing)} existing docs  ({sum(existing.values())} with first_rank)")

        # Upload / dry-run
        mode = "[DRY-RUN] " if args.dry_run else ""
        print(f"\n  {mode}Processing {len(records)} records ...")
        ins, upd, skp = upload_records(records, existing, args.dry_run, db)

        print(f"\n  Year {year} summary:")
        print(f"    Inserted : {ins}")
        print(f"    Updated  : {upd}  (added first_rank to existing records)")
        print(f"    Skipped  : {skp}  (already complete)")

        total_inserted += ins
        total_updated  += upd
        total_skipped  += skp

    print(f"\n{'='*60}")
    print(f"TOTAL ACROSS ALL YEARS:")
    print(f"  Inserted : {total_inserted}")
    print(f"  Updated  : {total_updated}")
    print(f"  Skipped  : {total_skipped}")
    if args.dry_run:
        print("\n[DRY-RUN] Nothing was written to Firestore.")


if __name__ == "__main__":
    main()
