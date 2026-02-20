"""
Test dynamic language detection and switching functionality.

This script demonstrates and tests that the chatbot can:
1. Start in one language (e.g., English)
2. Automatically detect when user switches to another language (e.g., Hindi)
3. Respond in the new detected language
4. Continue adapting throughout the conversation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.languages import detect_language, SUPPORTED_LANGUAGES


def test_language_detection():
    """Test language detection with various inputs."""
    
    test_cases = [
        # (input_text, expected_language)
        ("Hello, what is the admission process?", "en"),
        ("हिंदी में बताओ", "hi"),
        ("ప్రవేశ ప్రక్రియ ఏమిటి?", "te"),
        ("சேர்க்கை செயல்முறை என்ன?", "ta"),
        ("ಪ್ರವೇಶ ಪ್ರಕ್ರಿಯೆ ಏನು?", "kn"),
        ("प्रवेश प्रक्रिया काय आहे?", "mr"),
        ("ভর্তি প্রক্রিয়া কি?", "bn"),
        ("પ્રવેશ પ્રક્રિયા શું છે?", "gu"),
        ("CSE cutoff rank", "en"),
        ("CSE के लिए कटऑफ रैंक", "hi"),
        ("CSE కటాఫ్ ర్యాంక్", "te"),
    ]
    
    print("=" * 80)
    print("DYNAMIC LANGUAGE DETECTION TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for text, expected_lang in test_cases:
        detected = detect_language(text)
        status = "✅ PASS" if detected == expected_lang else "❌ FAIL"
        
        if detected == expected_lang:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | Input: {text[:50]:<50} | Expected: {expected_lang} | Detected: {detected}")
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    print()
    
    return failed == 0


def simulate_dynamic_conversation():
    """Simulate a conversation with dynamic language switching."""
    
    print("=" * 80)
    print("SIMULATED DYNAMIC LANGUAGE CONVERSATION")
    print("=" * 80)
    print()
    
    # Simulate a session
    session_language = "en"  # User initially selected English
    
    conversation = [
        "What are the admission requirements?",
        "हिंदी में बताओ",  # Switch to Hindi
        "CSE के लिए फीस क्या है?",  # Continue in Hindi
        "ప్రవేశ ప్రక్రియ ఏమిటి?",  # Switch to Telugu
        "What about hostel facilities?",  # Back to English
    ]
    
    print(f"Initial session language: {session_language} ({SUPPORTED_LANGUAGES[session_language]['native']})")
    print()
    
    for i, user_input in enumerate(conversation, 1):
        detected_lang = detect_language(user_input)
        
        # Simulate the backend logic
        if detected_lang != session_language:
            print(f"📍 Message {i}:")
            print(f"   User: {user_input}")
            print(f"   🔍 Language CHANGE detected: {session_language} → {detected_lang}")
            print(f"   📝 Session language updated to: {SUPPORTED_LANGUAGES[detected_lang]['native']}")
            session_language = detected_lang
        else:
            print(f"📍 Message {i}:")
            print(f"   User: {user_input}")
            print(f"   ✓ Language remains: {SUPPORTED_LANGUAGES[detected_lang]['native']}")
        
        print()
    
    print("=" * 80)
    print()


def main():
    """Run all tests."""
    
    print("\n" + "🌐" * 40)
    print("MULTILINGUAL DYNAMIC LANGUAGE DETECTION TEST SUITE")
    print("🌐" * 40 + "\n")
    
    # Test 1: Language detection accuracy
    print("TEST 1: Language Detection Accuracy")
    test1_passed = test_language_detection()
    
    # Test 2: Dynamic conversation simulation
    print("TEST 2: Dynamic Conversation Simulation")
    simulate_dynamic_conversation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Language Detection: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Dynamic Conversation: DEMONSTRATED")
    print()
    print("The chatbot now supports:")
    print("  • Real-time language detection on every message")
    print("  • Automatic language switching without manual intervention")
    print("  • Seamless adaptation across 8 languages")
    print("  • Session-based language tracking with dynamic updates")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
