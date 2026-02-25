"""
Backfill patch script: add first_rank and last_rank to existing Firestore records.

The old ingest code only stored 'cutoff_rank' (= closing/last rank) and discarded
the opening/first rank. This script re-extracts both columns from the original PDF
and patches just the first_rank / last_rank fields into existing documents using
Firestore merge, so no other fields are overwritten.

Usage (run from the project root with venv activated):
    python patch_first_rank.py --pdf "docs/pdfs/TGEAPCET24REVISED.pdf" --year 2024
    python patch_first_rank.py --pdf "docs/pdfs/TGEAPCET24REVISED.pdf" --year 2024 --dry-run
"""

from __future__ import annotations

import argparse
import json

from app.data.init_db import get_db, COLLECTION
from app.data.ingest_eapcet import extract_page, extract_special_pages, _doc_id


def patch_firestore(records: list[dict], dry_run: bool = False) -> None:
    """
    Patch first_rank and last_rank into existing Firestore documents.
    Uses merge=True so only these two fields are updated.
    """
    db = get_db()
    if db is None:
        print("[ERROR] Firestore not available.")
        return

    patched = 0
    skipped = 0
    batch = db.batch()
    batch_count = 0

    for rec in records:
        if rec.get("first_rank") is None:
            # Nothing new to add — skip
            skipped += 1
            continue

        doc_id = _doc_id(rec)
        doc_ref = db.collection(COLLECTION).document(doc_id)

        patch = {
            "first_rank": rec["first_rank"],
            "last_rank": rec.get("last_rank", rec.get("cutoff_rank")),
        }

        if dry_run:
            print(
                f"  [DRY-RUN] {doc_id:60s}  "
                f"first_rank={patch['first_rank']:>6,}  "
                f"last_rank={patch['last_rank']:>6,}"
            )
        else:
            batch.set(doc_ref, patch, merge=True)
            batch_count += 1
            if batch_count % 400 == 0:
                batch.commit()
                batch = db.batch()
                print(f"  ... committed {batch_count} patches so far ...")

        patched += 1

    if not dry_run and batch_count > 0:
        batch.commit()

    if dry_run:
        print(f"\n[DRY-RUN] Complete. Would patch {patched} records, skip {skipped} (no first_rank).")
    else:
        print(f"\n[OK] Patched {patched} Firestore documents with first_rank / last_rank.")
        if skipped:
            print(f"    Skipped {skipped} records that had no first_rank extracted.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill first_rank into Firestore cutoff documents.")
    parser.add_argument("--pdf", required=True, help="Path to the EAPCET cutoff PDF (e.g. docs/pdfs/TGEAPCET24REVISED.pdf)")
    parser.add_argument("--year", type=int, default=2024, help="Admission year encoded in the PDF (default: 2024)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be patched without writing to Firestore")
    args = parser.parse_args()

    print(f"[PDF] Reading: {args.pdf}  (year={args.year})")

    all_records: list[dict] = []

    # Extract regular pages (1, 2, 5)
    for pg in [0, 1, 4]:
        pg_label = pg + 1
        print(f"\n  Extracting page {pg_label} ...")
        try:
            recs = extract_page(args.pdf, page_num=pg, year=args.year)
            print(f"  -> {len(recs)} records extracted from page {pg_label}")
            fr_count = sum(1 for r in recs if r.get("first_rank") is not None)
            print(f"     ({fr_count} have first_rank populated)")
            all_records.extend(recs)
        except Exception as e:
            print(f"  [WARN] Page {pg_label} error: {e}")

    # Extract special-category pages (3, 4)
    print(f"\n  Extracting special-category pages (3-4) ...")
    try:
        special = extract_special_pages(args.pdf, year=args.year)
        print(f"  -> {len(special)} special records extracted")
        all_records.extend(special)
    except Exception as e:
        print(f"  [WARN] Special pages error: {e}")

    if not all_records:
        print("\n[ERROR] No records extracted. Check that the PDF path is correct.")
        return

    print(f"\n[INFO] Total extracted: {len(all_records)} records")
    first_rank_count = sum(1 for r in all_records if r.get("first_rank") is not None)
    print(f"       Records with first_rank: {first_rank_count}")

    # Show sample
    print("\nSample (first 5):")
    for r in all_records[:5]:
        print(
            f"  {r.get('branch'):12s} | {r.get('category'):6s} | {r.get('gender'):5s} "
            f"| first={r.get('first_rank', 'N/A'):>6}  last={r.get('last_rank', r.get('cutoff_rank', 'N/A')):>6}"
        )

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Patching Firestore ...")
    patch_firestore(all_records, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
