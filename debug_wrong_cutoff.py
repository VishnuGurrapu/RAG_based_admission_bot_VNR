"""Debug: Check ALL CSE BC-D 2023 records in database"""
from app.data.init_db import get_db, COLLECTION
from google.cloud.firestore_v1.base_query import FieldFilter

db = get_db()

# Query all CSE BC-D 2023 records (all genders, all quotas)
query = db.collection(COLLECTION)
query = query.where(filter=FieldFilter('year', '==', 2023))
query = query.where(filter=FieldFilter('branch', '==', 'CSE'))
query = query.where(filter=FieldFilter('category', '==', 'BC-D'))

docs = list(query.stream())
print(f"Found {len(docs)} CSE BC-D 2023 records\n")

for doc in docs:
    data = doc.to_dict()
    print(f"ID: {doc.id}")
    print(f"  Gender: {data.get('gender')}")
    print(f"  Quota: {data.get('quota')}")
    print(f"  Cutoff: {data.get('cutoff_rank')}")
    print(f"  First: {data.get('first_rank')}")
    print(f"  Last: {data.get('last_rank')}")
    print()

# Also check if there's a record with cutoff 1811
print("\n" + "=" * 70)
print("Searching for any record with cutoff_rank = 1811")
print("=" * 70)

query2 = db.collection(COLLECTION)
query2 = query2.where(filter=FieldFilter('cutoff_rank', '==', 1811))
docs2 = list(query2.stream())

if docs2:
    print(f"\nFound {len(docs2)} records with cutoff 1,811:")
    for doc in docs2:
        data = doc.to_dict()
        print(f"\nID: {doc.id}")
        print(f"  Branch: {data.get('branch')}")
        print(f"  Category: {data.get('category')}")
        print(f"  Gender: {data.get('gender')}")
        print(f"  Year: {data.get('year')}")
        print(f"  Quota: {data.get('quota')}")
else:
    print("\nNo records found with cutoff_rank = 1811")

# Check for 2023 as a cutoff rank
print("\n" + "=" * 70)
print("Searching for any record with cutoff_rank = 2023")
print("="  * 70)

query3 = db.collection(COLLECTION)
query3 = query3.where(filter=FieldFilter('cutoff_rank', '==', 2023))
docs3 = list(query3.stream())

if  docs3:
    print(f"\nFound {len(docs3)} records with cutoff 2,023:")
    for doc in docs3:
        data = doc.to_dict()
        print(f"\nID: {doc.id}")
        print(f"  Branch: {data.get('branch')}")
        print(f"  Category: {data.get('category')}")
        print(f"  Gender: {data.get('gender')}")
        print(f"  Year: {data.get('year')}")
else:
    print("\nNo records found with cutoff_rank = 2023")
