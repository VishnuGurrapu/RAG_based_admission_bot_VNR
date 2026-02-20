"""Test intent classification for cutoff queries"""
from app.classifier.intent_classifier import classify, IntentType

test_queries = [
    "what is the CSE cutoff for BC-D Girls in 2023?",
    "branches under the BC-D category (Girls) in 2023",
    "CSE cutoff 2023 BC-D Girls",
    "what was the closing rank for CSE in 2023 for BC-D girls?",
]

print("=" * 70)
print("TESTING INTENT CLASSIFICATION")
print("=" * 70)

for query in test_queries:
    result = classify(query)
    print(f"\nQuery: '{query}'")
    print(f"  Intent: {result.intent}")
    print(f"  Reason: {result.reason}")
    
    if result.intent not in (IntentType.CUTOFF, IntentType.MIXED):
        print(f"  ⚠️ WARNING: Should be CUTOFF or MIXED, got {result.intent}")
