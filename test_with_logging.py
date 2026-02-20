"""Test CSE BC-D Girls 2023 cutoff query with logging"""
import requests
import time

# Wait for server
time.sleep(3)

url = "http://localhost:8000/api/chat"
payload = {
    "message": "what is the CSE cutoff for BC-D Girls in 2023?",
    "session_id": "debug_session_001"
}

print("Sending query:", payload['message'])
print()

try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    reply = data.get("reply", "")
    
    print("Response:")
    print("=" * 70)
    print(reply)
    print("=" * 70)
    print()
    
    # Check values
    if "4,367" in reply:
        print("✅ CORRECT: Shows 4,367 (correct 2023 cutoff)")
    elif "1,811" in reply:
        print("❌ WRONG: Shows 1,811 (this is 2025 cutoff, not 2023)")
    
    if "2,023" in reply or "rank is 2,023" in reply:
        print("❌ WRONG: Treating 2023 as a rank")
    
    print(f"\nIntent: {data.get('intent')}")
    print(f"Sources: {data.get('sources')}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
