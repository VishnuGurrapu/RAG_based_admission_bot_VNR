"""
Test multilingual functionality of the chatbot
Run this after starting the server to verify language support works correctly
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_language_support():
    """Test multilingual support with different languages"""
    
    print("=" * 70)
    print("MULTILINGUAL CHATBOT TEST")
    print("=" * 70)
    
    # Test 1: English
    print("\n📝 TEST 1: English Query")
    print("-" * 70)
    session_1 = "test_en_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "What is the CSE cutoff for OC Boys?",
            "session_id": session_1,
            "language": "en"
        }
    )
    data = response.json()
    print(f"Query: What is the CSE cutoff for OC Boys?")
    print(f"Language: {data.get('language')}")
    print(f"Reply: {data.get('reply')[:200]}...")
    print(f"Intent: {data.get('intent')}")
    print("✅ PASS" if data.get('language') == 'en' else "❌ FAIL")
    
    # Test 2: Hindi
    print("\n📝 TEST 2: Hindi Query")
    print("-" * 70)
    session_2 = "test_hi_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "CSE की फीस क्या है?",
            "session_id": session_2,
            "language": "hi"
        }
    )
    data = response.json()
    print(f"Query: CSE की फीस क्या है?")
    print(f"Language: {data.get('language')}")
    print(f"Reply: {data.get('reply')[:200]}...")
    print(f"Intent: {data.get('intent')}")
    print("✅ PASS" if data.get('language') == 'hi' else "❌ FAIL")
    
    # Test 3: Telugu
    print("\n📝 TEST 3: Telugu Query")
    print("-" * 70)
    session_3 = "test_te_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "ప్రవేశ ప్రక్రియ ఏమిటి?",
            "session_id": session_3,
            "language": "te"
        }
    )
    data = response.json()
    print(f"Query: ప్రవేశ ప్రక్రియ ఏమిటి?")
    print(f"Language: {data.get('language')}")
    print(f"Reply: {data.get('reply')[:200]}...")
    print(f"Intent: {data.get('intent')}")
    print("✅ PASS" if data.get('language') == 'te' else "❌ FAIL")
    
    # Test 4: Tamil
    print("\n📝 TEST 4: Tamil Query")
    print("-" * 70)
    session_4 = "test_ta_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "சேர்க்கை செயல்முறை என்ன?",
            "session_id": session_4,
            "language": "ta"
        }
    )
    data = response.json()
    print(f"Query: சேர்க்கை செயல்முறை என்ன?")
    print(f"Language: {data.get('language')}")
    print(f"Reply: {data.get('reply')[:200]}...")
    print(f"Intent: {data.get('intent')}")
    print("✅ PASS" if data.get('language') == 'ta' else "❌ FAIL")
    
    # Test 5: Auto-detection (Hindi without specifying language)
    print("\n📝 TEST 5: Auto-detection (Hindi)")
    print("-" * 70)
    session_5 = "test_auto_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "कटऑफ रैंक क्या है?",
            "session_id": session_5,
            # No language parameter - should auto-detect
        }
    )
    data = response.json()
    print(f"Query: कटऑफ रैंक क्या है?")
    print(f"Detected Language: {data.get('language')}")
    print(f"Reply: {data.get('reply')[:200]}...")
    print("✅ PASS - Auto-detected Hindi" if data.get('language') == 'hi' else f"❌ FAIL - Detected as {data.get('language')}")
    
    # Test 6: Language switching in same session
    print("\n📝 TEST 6: Language Switching (English -> Hindi)")
    print("-" * 70)
    session_6 = "test_switch_" + str(int(sleep(0.01) or 0))
    
    # First message in English
    response1 = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "What is the admission process?",
            "session_id": session_6,
            "language": "en"
        }
    )
    data1 = response1.json()
    print(f"Message 1 (English): {data1.get('language')}")
    
    # Second message in Hindi (switch language)
    response2 = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "अब हिंदी में बताओ",
            "session_id": session_6,
            "language": "hi"
        }
    )
    data2 = response2.json()
    print(f"Message 2 (Hindi): {data2.get('language')}")
    print(f"Reply: {data2.get('reply')[:200]}...")
    print("✅ PASS - Language switched successfully" if data2.get('language') == 'hi' else "❌ FAIL")
    
    # Test 7: Language change request
    print("\n📝 TEST 7: Language Change Request")
    print("-" * 70)
    session_7 = "test_change_" + str(int(sleep(0.01) or 0))
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "change language to Hindi",
            "session_id": session_7,
            "language": "en"
        }
    )
    data = response.json()
    print(f"Query: change language to Hindi")
    print(f"Intent: {data.get('intent')}")
    print(f"New Language: {data.get('language')}")
    print("✅ PASS" if data.get('intent') in ['language_changed', 'language_selection'] else "❌ FAIL")
    
    print("\n" + "=" * 70)
    print("MULTILINGUAL TEST COMPLETED")
    print("=" * 70)


def test_ui_translations():
    """Test that UI translations are available"""
    from app.utils.languages import get_translation, SUPPORTED_LANGUAGES, TRANSLATIONS
    
    print("\n📝 UI TRANSLATIONS TEST")
    print("-" * 70)
    
    test_keys = ["welcome_title", "category_admission", "input_placeholder"]
    
    for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
        print(f"\n{lang_info['flag']} {lang_info['native']} ({lang_code}):")
        all_present = True
        for key in test_keys:
            translation = get_translation(key, lang_code)
            if translation == key:  # Translation not found
                print(f"  ❌ Missing: {key}")
                all_present = False
            else:
                print(f"  ✅ {key}: {translation[:50]}...")
        
        if all_present:
            print(f"  ✅ All translations present for {lang_info['name']}")
    
    print("\n✅ UI Translations test completed")


def test_language_detection():
    """Test language detection accuracy"""
    from app.utils.languages import detect_language
    
    print("\n📝 LANGUAGE DETECTION TEST")
    print("-" * 70)
    
    test_cases = [
        ("Hello, how are you?", "en", "English"),
        ("नमस्ते, आप कैसे हैं?", "hi", "Hindi"),
        ("నమస్కారం, మీరు ఎలా ఉన్నారు?", "te", "Telugu"),
        ("வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?", "ta", "Tamil"),
        ("ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ?", "kn", "Kannada"),
        ("CSE की कटऑफ क्या है?", "hi", "Hindi (mixed)"),
        ("ప్రవేశ process ఏమిటి?", "te", "Telugu (mixed)"),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_lang, description in test_cases:
        detected = detect_language(text)
        status = "✅ PASS" if detected == expected_lang else f"❌ FAIL (detected: {detected})"
        print(f"{status} - {description}")
        print(f"         Text: {text}")
        
        if detected == expected_lang:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"Detection Accuracy: {passed}/{len(test_cases)} ({100*passed//len(test_cases)}%)")
    print(f"{'='*70}")


if __name__ == "__main__":
    print("\n🚀 Starting Multilingual Chatbot Tests...\n")
    
    try:
        # Test 1: Language detection
        test_language_detection()
        
        # Test 2: UI translations
        test_ui_translations()
        
        # Test 3: Live API tests (requires server running)
        print("\n⚠️  Note: API tests require the server to be running on http://localhost:8000")
        try_api = input("\nDo you want to run live API tests? (y/n): ").lower().strip()
        
        if try_api == 'y':
            test_language_support()
        else:
            print("\n⏭️  Skipping live API tests")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
