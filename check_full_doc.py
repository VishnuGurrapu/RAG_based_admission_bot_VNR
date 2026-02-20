"""Check full document structure for BC-D Girls 2023"""
from app.data.init_db import get_db, COLLECTION
from google.cloud.firestore_v1.base_query import FieldFilter
import json

db = get_db()
query = db.collection(COLLECTION)
query = query.where(filter=FieldFilter('year', '==', 2023))
query = query.where(filter=FieldFilter('category', '==', 'BC-D'))
query = query.where(filter=FieldFilter('gender', '==', 'Girls'))

docs = list(query.stream())
print(f'Total BC-D Girls 2023 records: {len(docs)}\n')

if docs:
    print('Full structure of first document:')
    print(json.dumps(docs[0].to_dict(), indent=2, default=str))
    
    # Check if any records have non-None ranks
    print('\n\nRecords with valid ranks:')
    for doc in docs:
        data = doc.to_dict()
        if data.get('first_rank') or data.get('last_rank') or data.get('cutoff_rank'):
            print(json.dumps(data, indent=2, default=str))
