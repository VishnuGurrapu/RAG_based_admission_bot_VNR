"""
Cutoff engine – exact eligibility computation from Firestore.

This module NEVER approximates.  If data is missing it says so.
"""

from __future__ import annotations

import logging
import sys
import traceback

logger = logging.getLogger("app.logic.cutoff_engine")
logger.info("cutoff_engine.py: starting imports...")

from dataclasses import dataclass, field
from typing import Optional

logger.info("cutoff_engine.py: importing google.cloud.firestore_v1...")
try:
    from google.cloud.firestore_v1.base_query import FieldFilter
    logger.info("cutoff_engine.py: google.cloud.firestore_v1 OK")
except Exception as e:
    logger.error(f"cutoff_engine.py: FAILED google.cloud.firestore_v1: {e}")
    traceback.print_exc()
    raise

logger.info("cutoff_engine.py: importing init_db...")
try:
    from app.data.init_db import get_db, COLLECTION
    logger.info("cutoff_engine.py: init_db OK")
except Exception as e:
    logger.error(f"cutoff_engine.py: FAILED init_db: {e}")
    traceback.print_exc()
    raise

logger.info("cutoff_engine.py: importing config...")
try:
    from app.config import get_settings
    logger.info("cutoff_engine.py: config OK")
except Exception as e:
    logger.error(f"cutoff_engine.py: FAILED config: {e}")
    traceback.print_exc()
    raise


@dataclass
class CutoffResult:
    eligible: Optional[bool] = None
    cutoff_rank: Optional[int] = None
    branch: Optional[str] = None
    category: Optional[str] = None
    year: Optional[int] = None
    round: Optional[int] = None
    gender: Optional[str] = None
    quota: Optional[str] = None
    message: str = ""
    all_results: list[dict] = field(default_factory=list)


def _get_department_url(branch: str) -> str | None:
    """
    Get the department URL for a given branch.
    Maps normalized branch codes to department pages.
    """
    settings = get_settings()
    dept_urls = settings.DEPARTMENT_URLS
    
    # Mapping of branch codes to department URL keys
    branch_mapping = {
        # CSE variants
        "CSE": "cse",
        "CSB": "cse",  # CS & Business Systems under CSE
        
        # AI/ML/IoT specializations
        "CSE-CSM": "cse_aiml_iot",  # AI & ML
        "CSE-CSO": "cse_aiml_iot",  # IoT
        "RAI": "cse_aiml_iot",      # Robotics & AI
        
        # Data Science/Cyber Security
        "CSE-CSD": "cse_ds_cys",  # Data Science
        "AID": "cse_ds_cys",       # AI & Data Science
        "CSE-CSC": "cse_ds_cys",  # Cyber Security
        
        # Other departments
        "IT": "it",
        "ME": "mech",
        "AUT": "automobile",  # Automobile Engineering
        "BIO": "biotechnology",  # Biotechnology
        "CIV": "civil",
        "ECE": "ece",
        "EEE": "eee",
        "EIE": "eie",
    }
    
    dept_key = branch_mapping.get(branch)
    if dept_key:
        return dept_urls.get(dept_key)
    return None


def _normalise_branch(raw: str) -> str:
    """Best-effort normalisation of branch names."""
    mapping = {
        "computer science": "CSE",
        "computer": "CSE",
        "cse": "CSE",
        "cs": "CSE",
        "ece": "ECE",
        "electronics": "ECE",
        "electronics communication": "ECE",
        "eee": "EEE",
        "electrical": "EEE",
        "electrical electronics": "EEE",
        "it": "IT",
        "information technology": "IT",
        "mech": "ME",
        "me": "ME",
        "mechanical": "ME",
        "civil": "CIV",
        "civ": "CIV",
        
        # AI & ML variants (CSE-CSM)
        "ai ml": "CSE-CSM",
        "ai & ml": "CSE-CSM",
        "aiml": "CSE-CSM",
        "ai and ml": "CSE-CSM",
        "artificial intelligence ml": "CSE-CSM",
        "artificial intelligence machine learning": "CSE-CSM",
        "artificial intelligence and machine learning": "CSE-CSM",
        "machine learning": "CSE-CSM",
        
        # AI & Data Science variants (AID)
        "ai & ds": "AID",
        "ai ds": "AID",
        "aids": "AID",
        "ai and ds": "AID",
        "ai & data science": "AID",
        "ai and data science": "AID",
        "artificial intelligence data science": "AID",
        "artificial intelligence and data science": "AID",
        
        # Data Science variants (CSE-CSD)
        "data science": "CSE-CSD",
        "ds": "CSE-CSD",
        "csd": "CSE-CSD",
        "cse-csd": "CSE-CSD",
        "cse csd": "CSE-CSD",
        "cse (data science)": "CSE-CSD",
        
        # AI/ML/IoT combined
        "csm": "CSE-CSM",
        "cse-csm": "CSE-CSM",
        "cse csm": "CSE-CSM",
        "cse (ai & ml)": "CSE-CSM",
        
        # Cyber Security
        "csc": "CSE-CSC",
        "cse-csc": "CSE-CSC",
        "cse csc": "CSE-CSC",
        "cyber security": "CSE-CSC",
        "cys": "CSE-CSC",
        "cybersecurity": "CSE-CSC",
        
        # IoT
        "cso": "CSE-CSO",
        "cse-cso": "CSE-CSO",
        "cse cso": "CSE-CSO",
        "iot": "CSE-CSO",
        "internet of things": "CSE-CSO",
        
        # Business Systems
        "csb": "CSB",
        "cs business": "CSB",
        "business systems": "CSB",
        "aid": "AID",
        "aut": "AUT",
        "automobile": "AUT",
        "bio": "BIO",
        "biotech": "BIO",
        "biotechnology": "BIO",
        "eie": "EIE",
        "rai": "RAI",
        "robotics": "RAI",
        "robotics & ai": "RAI",
        "vlsi": "VLSI",
    }
    return mapping.get(raw.strip().lower(), raw.strip().upper())


def _normalise_category(raw: str) -> str:
    mapping = {
        "oc": "OC",
        "general": "OC",
        "open": "OC",
        "obc": "BC-D",
        "bc-a": "BC-A",
        "bc-b": "BC-B",
        "bc-c": "BC-C",
        "bc-d": "BC-D",
        "bc-e": "BC-E",
        "bca": "BC-A",
        "bcb": "BC-B",
        "bcc": "BC-C",
        "bcd": "BC-D",
        "bce": "BC-E",
        "sc": "SC",
        "sc-i": "SC-I",
        "sc-ii": "SC-II",
        "sc-iii": "SC-III",
        "sc-1": "SC-I",
        "sc-2": "SC-II",
        "sc-3": "SC-III",
        "sc1": "SC-I",
        "sc2": "SC-II",
        "sc3": "SC-III",
        "st": "ST",
        "ews": "EWS",
    }
    return mapping.get(raw.strip().lower(), raw.strip().upper())


def get_cutoff(
    branch: str,
    category: str,
    year: int | None = None,
    round_num: int | None = None,
    gender: str = "Any",
    quota: str = "Convenor",
    ph_type: str | None = None,
    show_trend: bool = False,
) -> CutoffResult:
    """
    Look up exact cutoff from Firestore.

    Parameters
    ----------
    branch : str  – e.g. "CSE", "ECE", "IT"
    category : str – e.g. "OC", "BC-A", "SC"
    year : int     – counselling year (defaults to latest available)
    round_num : int – counselling round (defaults to latest)
    gender : str   – "Boys" | "Girls"
    quota : str    – "Convenor" | "SPORTS" | "CAP" | "NCC" | "OTHERS"
    ph_type : str  – PH disability code: "PHV","PHH","PHO","PHM","PHA" or None
    show_trend : bool – If True, show all years with trend analysis; if False, show only latest year
    """
    logger.info(f"get_cutoff called: branch={branch}, category={category}, year={year}, gender={gender}, quota={quota}")
    branch = _normalise_branch(branch)
    category = _normalise_category(category)

    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Cannot query cutoff data.")
        return CutoffResult(
            message="⚠️ Cutoff database is currently unavailable. Please try general admission questions instead, or contact admissionsenquiry@vnrvjiet.in for cutoff information.",
            found=False,
        )

    query = db.collection(COLLECTION)

    # Build Firestore query with compound filters
    query = query.where(filter=FieldFilter("branch", "==", branch))
    query = query.where(filter=FieldFilter("category", "==", category))
    query = query.where(filter=FieldFilter("gender", "==", gender))
    query = query.where(filter=FieldFilter("quota", "==", quota))

    if ph_type:
        query = query.where(filter=FieldFilter("ph_type", "==", ph_type))

    if year:
        query = query.where(filter=FieldFilter("year", "==", year))
    if round_num:
        query = query.where(filter=FieldFilter("round", "==", round_num))

    docs = query.stream()
    rows = [doc.to_dict() for doc in docs]
    
    logger.info(f"Firestore query returned {len(rows)} rows for branch={branch}, category={category}, gender={gender}, year={year}")
    if rows:
        logger.info(f"Sample row: {rows[0]}")

    # Also check with 'caste' field for older EWS records that use that name
    if not rows or category == "EWS":
        alt_query = db.collection(COLLECTION)
        alt_query = alt_query.where(filter=FieldFilter("branch", "==", branch))
        alt_query = alt_query.where(filter=FieldFilter("caste", "==", category))
        alt_query = alt_query.where(filter=FieldFilter("gender", "==", gender))
        alt_query = alt_query.where(filter=FieldFilter("quota", "==", quota))
        if year:
            alt_query = alt_query.where(filter=FieldFilter("year", "==", year))
        alt_docs = alt_query.stream()
        for doc in alt_docs:
            d = doc.to_dict()
            # Normalize: map old field names to new ones
            if "caste" in d and "category" not in d:
                d["category"] = d["caste"]
            if "cutoff_rank" not in d:
                d["cutoff_rank"] = d.get("last_rank") or d.get("first_rank")
            if d.get("cutoff_rank") is not None:
                rows.append(d)

    # Sort: latest year first, then latest round
    rows.sort(key=lambda r: (r.get("year", 0), r.get("round", 0)), reverse=True)

    if not rows:
        return CutoffResult(
            branch=branch,
            category=category,
            year=year,
            round=round_num,
            message=(
                f"No cutoff data found for {branch} / {category}"
                + (f" / {year}" if year else "")
                + (f" / Round {round_num}" if round_num else "")
                + ". The data may not be available yet."
            ),
        )

    best = rows[0]

    # If no specific year requested and show_trend=True, show ALL available years with analysis
    if not year and show_trend and len(set(r.get("year") for r in rows)) > 1:
        # Group by year and build a year-wise comparison
        years_seen = {}
        for r in rows:
            y = r.get("year")
            if y and y not in years_seen:
                years_seen[y] = r
        sorted_years = sorted(years_seen.keys())

        year_lines = []
        ranks_list = []
        for y in sorted_years:
            r = years_seen[y]
            rank = r.get("cutoff_rank", 0)
            year_lines.append(f"• **{y}**: Closing rank **{rank:,}**")
            ranks_list.append(rank)

        # Analyze trend
        trend_analysis = ""
        if len(ranks_list) >= 2:
            first_rank = ranks_list[0]
            last_rank = ranks_list[-1]
            diff = last_rank - first_rank
            pct_change = (diff / first_rank * 100) if first_rank > 0 else 0
            
            if abs(pct_change) < 5:
                trend_analysis = (
                    f"\n\n📊 **Trend Analysis:** The cutoff has remained relatively stable over the years "
                    f"(~{abs(pct_change):.1f}% change). This branch maintains consistent demand."
                )
            elif diff < 0:  # Rank decreased (became more competitive)
                trend_analysis = (
                    f"\n\n📊 **Trend Analysis:** The cutoff rank has **decreased by {abs(pct_change):.1f}%** "
                    f"from {sorted_years[0]} to {sorted_years[-1]}, indicating **rising competition**. "
                    f"The branch is becoming more sought-after. Plan accordingly and consider backup options."
                )
            else:  # Rank increased (became less competitive)
                trend_analysis = (
                    f"\n\n📊 **Trend Analysis:** The cutoff rank has **increased by {pct_change:.1f}%** "
                    f"from {sorted_years[0]} to {sorted_years[-1]}, indicating **improving chances**. "
                    f"Competition has eased slightly, making admission more accessible than before."
                )

        # Add department URL suggestion
        dept_url = _get_department_url(branch)
        dept_link = f"\n\n🔗 **Explore {branch} Department:** {dept_url}" if dept_url else ""
        
        message = (
            f"Here are the cutoff ranks for **{branch}** under **{category}** "
            f"category ({gender}, {quota} quota) across all available years:\n\n"
            + "\n".join(year_lines)
            + trend_analysis
            + dept_link
            + "\n\n⚠️ _These are based on previous year data and cutoffs may vary._"
        )
    else:
        # Show only the latest year (default behavior)
        year_label = f"**{best['year']}**" if best.get('year') else "the latest year"
        
        # Add department URL suggestion
        dept_url = _get_department_url(branch)
        dept_link = f"\n\n🔗 **Explore {branch} Department:** {dept_url}" if dept_url else ""
        
        message = (
            f"The closing cutoff rank for **{best['branch']}** under **{best['category']}** "
            f"category in {year_label}, Round {best.get('round', 1)} "
            f"({best['quota']} quota) is **{best['cutoff_rank']:,}**."
            + dept_link
            + "\n\n⚠️ _This is based on previous year data and cutoffs may vary._"
        )

    return CutoffResult(
        cutoff_rank=best["cutoff_rank"],
        branch=best.get("branch", branch),
        category=best.get("category", category),
        year=best.get("year"),
        round=best.get("round"),
        gender=best.get("gender", gender),
        quota=best.get("quota", quota),
        message=message,
        all_results=rows,
    )


def check_eligibility(
    rank: int,
    branch: str,
    category: str,
    year: int | None = None,
    round_num: int | None = None,
    gender: str = "Boys",
) -> CutoffResult:
    """
    Check if a given rank qualifies for a branch + category.
    Uses the latest available year/round if not specified.
    """
    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Cannot check eligibility.")
        return CutoffResult(
            message="⚠️ Cutoff database is currently unavailable. Please try general admission questions instead, or contact admissionsenquiry@vnrvjiet.in for eligibility information.",
            found=False,
        )
    
    result = get_cutoff(branch, category, year, round_num, gender=gender)

    if result.cutoff_rank is None:
        result.eligible = None
        return result

    result.eligible = rank <= result.cutoff_rank

    # Add department URL suggestion
    dept_url = _get_department_url(result.branch)
    dept_link = f"\n\n🔗 **Explore {result.branch} Department:** {dept_url}" if dept_url else ""

    if result.eligible:
        result.message = (
            f"With a rank of **{rank:,}**, you are **eligible** for "
            f"{result.branch} under {result.category} category ({result.gender}) "
            f"based on Year {result.year}, Round {result.round} ({result.quota} quota) cutoffs. "
            f"The closing rank was **{result.cutoff_rank:,}**."
            + dept_link
            + "\n\n⚠️ _This is based on previous year data. Actual cutoffs may vary this year._"
        )
    else:
        result.message = (
            f"With a rank of **{rank:,}**, you are **not eligible** for "
            f"{result.branch} under {result.category} category ({result.gender}) "
            f"based on Year {result.year}, Round {result.round} ({result.quota} quota) cutoffs. "
            f"The closing rank was **{result.cutoff_rank:,}**. "
            f"Your rank needs to be ≤ {result.cutoff_rank:,} for this seat."
            + dept_link
            + "\n\n⚠️ _This is based on previous year data. Actual cutoffs may vary this year._"
        )

    return result


def list_branches() -> list[str]:
    """Return all distinct branches in Firestore."""
    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Returning default branch list.")
        # Return common branches as fallback
        return ["CSE", "ECE", "EEE", "ME", "CIV", "IT", "CSE-CSM", "AID"]
    
    docs = db.collection(COLLECTION).stream()
    branches = sorted({doc.to_dict().get("branch", "") for doc in docs})
    return [b for b in branches if b]


def list_categories() -> list[str]:
    """Return all distinct categories in Firestore."""
    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Returning default category list.")
        return ["OC", "BC-A", "BC-B", "BC-C", "BC-D", "SC", "ST", "EWS"]
    
    docs = db.collection(COLLECTION).stream()
    cats = sorted({doc.to_dict().get("category", "") for doc in docs})
    return [c for c in cats if c]


def get_all_cutoffs_for_branch(
    branch: str, year: int | None = None
) -> list[dict]:
    """Return every document for a branch (all categories/rounds)."""
    branch = _normalise_branch(branch)
    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Cannot get cutoffs.")
        return []
    
    query = db.collection(COLLECTION).where(
        filter=FieldFilter("branch", "==", branch)
    )

    if year:
        query = query.where(filter=FieldFilter("year", "==", year))

    docs = query.stream()
    rows = [doc.to_dict() for doc in docs]
    rows.sort(
        key=lambda r: (r.get("year", 0), r.get("category", ""), r.get("round", 0)),
        reverse=True,
    )
    return rows


def get_cutoffs_flexible(
    branch: str | None = None,
    category: str | None = None,
    gender: str | None = None,
    year: int | None = None,
    round_num: int | None = None,
    quota: str = "Convenor",
    limit: int = 100,
) -> list[dict]:
    """
    Flexible cutoff query that allows filtering by any combination of parameters.
    Use None or omit parameters to get all values for that dimension.
    
    Parameters
    ----------
    branch : str | None – Specific branch code or None for all branches
    category : str | None – Specific category or None for all categories
    gender : str | None – "Boys", "Girls", or None for all genders
    year : int | None – Specific year or None for latest/all years
    round_num : int | None – Specific round or None for all rounds
    quota : str – "Convenor", "SPORTS", etc.
    limit : int – Maximum number of results to return
    
    Returns
    -------
    list[dict] : List of cutoff records matching the criteria
    """
    logger.info(f"get_cutoffs_flexible called: branch={branch}, category={category}, gender={gender}, year={year}")
    
    # Normalize inputs if provided
    if branch:
        branch = _normalise_branch(branch)
    if category:
        category = _normalise_category(category)
    
    db = get_db()
    if db is None:
        logger.warning("Firestore not available. Cannot query cutoff data.")
        return []

    query = db.collection(COLLECTION)

    # Apply filters only for non-None parameters
    if branch:
        query = query.where(filter=FieldFilter("branch", "==", branch))
    if category:
        query = query.where(filter=FieldFilter("category", "==", category))
    if gender:
        query = query.where(filter=FieldFilter("gender", "==", gender))
    if quota:
        query = query.where(filter=FieldFilter("quota", "==", quota))
    if year:
        query = query.where(filter=FieldFilter("year", "==", year))
    if round_num:
        query = query.where(filter=FieldFilter("round", "==", round_num))

    # Fetch documents
    docs = query.limit(limit).stream()
    rows = [doc.to_dict() for doc in docs]
    
    logger.info(f"get_cutoffs_flexible returned {len(rows)} rows")
    
    # Handle old 'caste' field for EWS records
    if category == "EWS" or not category:
        alt_query = db.collection(COLLECTION)
        if branch:
            alt_query = alt_query.where(filter=FieldFilter("branch", "==", branch))
        if category:
            alt_query = alt_query.where(filter=FieldFilter("caste", "==", category))
        if gender:
            alt_query = alt_query.where(filter=FieldFilter("gender", "==", gender))
        if quota:
            alt_query = alt_query.where(filter=FieldFilter("quota", "==", quota))
        if year:
            alt_query = alt_query.where(filter=FieldFilter("year", "==", year))
        
        alt_docs = alt_query.limit(limit).stream()
        for doc in alt_docs:
            d = doc.to_dict()
            # Normalize old field names
            if "caste" in d and "category" not in d:
                d["category"] = d["caste"]
            if "cutoff_rank" not in d:
                d["cutoff_rank"] = d.get("last_rank") or d.get("first_rank")
            if d.get("cutoff_rank") is not None and d not in rows:
                rows.append(d)
    
    # Sort by year (desc), branch, category, round (desc)
    rows.sort(
        key=lambda r: (
            r.get("year", 0),
            r.get("branch", ""),
            r.get("category", ""),
            r.get("round", 0)
        ),
        reverse=True,
    )
    
    return rows


def format_cutoffs_table(
    cutoffs: list[dict],
    title: str = "Cutoff Ranks",
    max_rows: int = 50,
) -> str:
    """
    Format a list of cutoff records into a readable table/message.
    
    Parameters
    ----------
    cutoffs : list[dict] – Cutoff records from get_cutoffs_flexible
    title : str – Title for the table
    max_rows : int – Maximum rows to display
    
    Returns
    -------
    str : Formatted message with cutoff data
    """
    if not cutoffs:
        return "No cutoff data found for the specified criteria. The data may not be available yet."
    
    # Group by branch for better readability
    by_branch = {}
    for row in cutoffs[:max_rows]:
        branch = row.get("branch", "Unknown")
        if branch not in by_branch:
            by_branch[branch] = []
        by_branch[branch].append(row)
    
    lines = [f"## {title}\n"]
    
    for branch, records in by_branch.items():
        lines.append(f"\n### {branch}")
        
        # Group by year within branch
        by_year = {}
        for rec in records:
            year = rec.get("year", "N/A")
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(rec)
        
        for year in sorted(by_year.keys(), reverse=True):
            year_records = by_year[year]
            lines.append(f"\n**Year {year}:**")
            
            for rec in year_records:
                category = rec.get("category", "N/A")
                gender = rec.get("gender", "N/A")
                rank = rec.get("cutoff_rank", rec.get("last_rank", "N/A"))
                round_num = rec.get("round", "N/A")
                quota = rec.get("quota", "Convenor")
                
                if isinstance(rank, (int, float)):
                    rank_str = f"{int(rank):,}"
                else:
                    rank_str = str(rank)
                
                lines.append(
                    f"- **{category}** ({gender}) - Round {round_num}: **{rank_str}** ({quota} quota)"
                )
    
    if len(cutoffs) > max_rows:
        lines.append(f"\n\n_Showing first {max_rows} of {len(cutoffs)} results._")
    
    lines.append("\n\n⚠️ _These are based on previous year data and cutoffs may vary._")
    
    return "\n".join(lines)
