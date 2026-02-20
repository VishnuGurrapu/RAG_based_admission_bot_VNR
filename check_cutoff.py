"""Quick script to check BC-D Girls 2023 cutoff data"""
from app.data.init_db import get_db, COLLECTION
from google.cloud.firestore_v1.base_query import FieldFilter
import json

db = get_db()
query = db.collection(COLLECTION)
query = query.where(filter=FieldFilter('year', '==', 2023))
query = query.where(filter=FieldFilter('category', '==', 'BC-D'))
query = query.where(filter=FieldFilter('gender', '==', 'Girls'))

docs = list(query.stream())
print(f'Total BC-D Girls 2023 records: {len(docs)}')
print('\nSample records:')
for doc in docs[:15]:
    data = doc.to_dict()
    print(f"Branch: {data.get('branch')}, First: {data.get('first_rank')}, Last: {data.get('last_rank')}")
