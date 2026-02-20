"""Final comprehensive test"""
import requests
import time

time.sleep(1)

url = "http://localhost:8000/api/chat"

tests = [
    {
        "message": "Show me all BC-D Girls cutoffs for 2023",
        "session": "final_test_1",
        "expected": ["4,367", "17,178", "40,750"],  # CSE, ECE, EEE cutoffs
        "should_not_contain": ["1,811", "2,023", "rank is 2,023"]
    },
    {
        "message": "What was the ECE cutoff for BC-D Girls in 2023?",
        "session": "final_test_2",
        "expected": ["17,178"],
        "should_not_contain": ["2,023", "rank is 2,023"]
    }
]

for i, test in enumerate(tests, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}: {test['message']}")
    print('='*70)
    
    payload = {
        "message": test['message'],
        "session_id": test['session']
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        reply = data.get("reply", "")
        
        print(f"\nResponse (first 500 chars):")
        print(reply[:500])
        print()
        
        # Check expected values
        found_expected = [val for val in test['expected'] if val in reply]
        if found_expected:
            print(f"✅ Found expected values: {found_expected}")
        else:
            print(f"❌ Missing expected values: {test['expected']}")
        
        # Check should not contain
        found_bad = [val for val in test['should_not_contain'] if val in reply]
        if found_bad:
            print(f"❌ Found incorrect values: {found_bad}")
        else:
            print(f"✅ No incorrect values found")
        
        print(f"\nIntent: {data.get('intent')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)
