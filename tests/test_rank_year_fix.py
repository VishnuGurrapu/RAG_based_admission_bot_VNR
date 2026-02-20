"""Test the rank/year extraction fixes"""
from app.utils.validators import extract_rank, extract_year

# Test cases for extract_rank
test_cases_rank = [
    ("my rank is 15000", 15000, "Normal rank"),
    ("I got 42000 rank", 42000, "Normal rank in middle of sentence"),
    ("21k rank", 21000, "Rank with k notation"),
    ("rank 2023", None, "Year 2023 should NOT be extracted as rank"),
    ("2024 cutoff", None, "Year 2024 should NOT be extracted as rank"),
    ("what about 2025", None, "Year 2025 should NOT be extracted as rank"),
    ("branches in 2022", None, "Year 2022 should NOT be extracted as rank"),
    ("2020 data", None, "Year 2020 should NOT be extracted as rank"),
    ("rank is 2019", 2019, "2019 is a valid rank (not in year range)"),
    ("rank is 2031", 2031, "2031 is a valid rank (not in year range)"),
]

# Test cases for extract_year
test_cases_year = [
    ("cutoff in 2023", 2023, "Year 2023"),
    ("2024 admissions", 2024, "Year 2024"),
    ("what about 2025?", 2025, "Year 2025"),
    ("rank is 15000", None, "No year present"),
    ("branches available", None, "No year present"),
]

print("=" * 70)
print("TESTING extract_rank() - Should exclude years 2020-2030")
print("=" * 70)
for query, expected, description in test_cases_rank:
    result = extract_rank(query)
    status = "✓" if result == expected else "✗"
    print(f"{status} {description}")
    print(f"  Query: '{query}'")
    print(f"  Expected: {expected}, Got: {result}")
    if result != expected:
        print(f"  ❌ FAILED!")
    print()

print("\n" + "=" * 70)
print("TESTING extract_year() - Should extract years 2020-2030")
print("=" * 70)
for query, expected, description in test_cases_year:
    result = extract_year(query)
    status = "✓" if result == expected else "✗"
    print(f"{status} {description}")
    print(f"  Query: '{query}'")
    print(f"  Expected: {expected}, Got: {result}")
    if result != expected:
        print(f"  ❌ FAILED!")
    print()

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
rank_passed = sum(1 for q, e, _ in test_cases_rank if extract_rank(q) == e)
year_passed = sum(1 for q, e, _ in test_cases_year if extract_year(q) == e)
total_passed = rank_passed + year_passed
total_tests = len(test_cases_rank) + len(test_cases_year)

print(f"Rank extraction tests: {rank_passed}/{len(test_cases_rank)} passed")
print(f"Year extraction tests: {year_passed}/{len(test_cases_year)} passed")
print(f"Total: {total_passed}/{total_tests} passed")

if total_passed == total_tests:
    print("\n✅ ALL TESTS PASSED!")
else:
    print(f"\n❌ {total_tests - total_passed} tests failed")
