# Multilingual Support Documentation

## Overview

The VNRVJIET Admissions Chatbot now supports **multiple languages**, allowing users to interact in their preferred language. The system automatically detects the user's language and responds accordingly.

## Supported Languages

| Language | Code | Native Name | Status |
|----------|------|-------------|---------|
| English  | `en` | English     | ✅ Fully Supported |
| Hindi    | `hi` | हिन्दी      | ✅ Fully Supported |
| Telugu   | `te` | తెలుగు      | ✅ Fully Supported |
| Tamil    | `ta` | தமிழ்       | ✅ Fully Supported |
| Marathi  | `mr` | मराठी       | ✅ Fully Supported |
| Kannada  | `kn` | ಕನ್ನಡ       | ✅ Fully Supported |
| Bengali  | `bn` | বাংলা       | ✅ Fully Supported |
| Gujarati | `gu` | ગુજરાતી     | ✅ Fully Supported |

## Features

### 1. Language Selection on First Visit
- When a user opens the chatbot for the first time, they are presented with a language selector
- Users can choose their preferred language from the available options
- The language preference is saved in the browser's session storage

### 2. Automatic Language Detection
- If a user types a message in a specific language, the system auto-detects it
- The chatbot automatically switches to respond in the detected language
- Detection works for all supported languages using character ranges and common keywords

### 3. Session-Based Language Preference
- Language preference is maintained throughout the user's session
- Each session ID is associated with a specific language preference
- Language preference persists across page refreshes within the same browser session

### 4. Dynamic Language Switching
- Users can change language mid-conversation
- Click the "🌐 Change Language" button to access the language selector again
- All subsequent responses will be in the newly selected language
- Conversation history is preserved when switching languages

### 5. Multilingual UI Elements
All user interface elements are translated, including:
- Welcome messages
- Category buttons (Admissions, Cutoff, Documents, Fees)
- Input placeholder text
- Error messages
- System prompts

### 6. Multilingual Bot Responses
- The bot generates responses in the user's selected language
- Technical terms (branch names, numbers, etc.) remain in English for clarity
- All explanations and conversational text are fully translated

## Technical Implementation

### Backend (`app/api/chat.py`)

The backend has been enhanced with:

#### Language State Management
```python
_session_language: dict[str, str] = {}  # Stores language preference per session
```

#### Request & Response Models
```python
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    language: str | None = None  # User's preferred language code

class ChatResponse(BaseModel):
    reply: str
    intent: str
    session_id: str
    sources: list[str] = []
    language: str = "en"  # Current language for this session
```

#### Language Detection & Switching
- Automatically detects language from user input using character ranges
- Supports explicit language change requests
- Shows language selector when requested

#### LLM Response Generation
- System prompt is enhanced with language-specific instructions
- Responses are generated in the user's preferred language
- Uses `get_language_instruction()` to inject language directives

### Frontend (`app/frontend/widget.js`)

The frontend includes:

#### State Management
```javascript
let currentLanguage = sessionStorage.getItem("chatbot_language") || "en";
let languageSelected = sessionStorage.getItem("chatbot_language_selected") === "true";
```

#### Language Selector UI
- Beautiful grid-based language selector with flags
- Displays native language names
- Hover effects for better UX

#### Translation System
```javascript
const TRANSLATIONS = {
  welcome_title: {
    en: "Hello! 👋 Welcome to the **VNRVJIET** assistant.",
    hi: "नमस्ते! 👋 **VNRVJIET** सहायक में आपका स्वागत है।",
    // ... more languages
  },
  // ... more translation keys
};

function t(key) {
  return TRANSLATIONS[key]?.[currentLanguage] || TRANSLATIONS[key]?.en || key;
}
```

#### API Communication
- Sends `language` parameter with every request
- Updates local language state when backend changes it
- Displays error messages in user's language

### Language Utilities (`app/utils/languages.py`)

A dedicated module handles all language-related functionality:

#### Language Detection
```python
def detect_language(text: str) -> str:
    """Detect language from text using character ranges and common words."""
```

- Uses Unicode character ranges to identify languages
- Falls back to keyword matching for accuracy
- Returns language code (e.g., 'hi', 'te', 'ta')

#### Language Change Detection
```python
def detect_language_change_request(text: str, current_language: str) -> Optional[str]:
    """Detect if user is requesting to change language."""
```

- Recognizes language change keywords in multiple languages
- Returns new language code or `"show_selector"` to display language options

#### Translation Retrieval
```python
def get_translation(key: str, language: str = "en") -> str:
    """Get translated text for a given key and language."""
```

- Provides translations for UI elements and system messages
- Falls back to English if translation not found

#### Language Instructions for LLM
```python
def get_language_instruction(language: str) -> str:
    """Get instruction to add to system prompt for the specified language."""
```

- Returns language-specific instructions for the AI model
- Ensures consistent responses in the target language

## Usage Examples

### Example 1: First-Time User

**User opens chatbot**
```
Bot: Please select your preferred language:
     🇬🇧 English
     🇮🇳 हिन्दी (Hindi)
     🇮🇳 తెలుగు (Telugu)
     ... more options
```

**User selects Telugu**
```
Bot: నమస్కారం! 👋 VNRVJIET సహాయకునికి స్వాగతం.
     నేను ఈ క్రింది అంశాలలో మీకు సహాయం చేయగలను. దయచేసి ఒకదాన్ని ఎంచుకోండి:
     [ప్రవేశ ప్రక్రియ & అర్హత]
     [బ్రాంచ్-వారీ కటాఫ్ ర్యాంక్‌లు]
     ... more categories
```

### Example 2: Language Switching Mid-Conversation

**User in English**
```
User: What is the CSE cutoff?
Bot: The cutoff for Computer Science Engineering (CSE) for OC Boys in 2024 is...
```

**User clicks "🌐 Change Language" and selects Hindi**
```
User: हिन्दी (selects)
Bot: नमस्ते! 👋 VNRVJIET सहायक में आपका स्वागत है.
     मैं निम्नलिखित विषयों में आपकी मदद कर सकता/सकती हूं...
```

**Conversation continues in Hindi**
```
User: CSE के लिए फीस क्या है?
Bot: कंप्यूटर साइंस इंजीनियरिंग (CSE) के लिए वार्षिक शुल्क...
```

### Example 3: Auto-Detection

**User types in Tamil without selecting language**
```
User: சேர்க்கை செயல்முறை என்ன?
Bot: (auto-detects Tamil)
     சேர்க்கை செயல்முறை பற்றிய தகவல்கள்:
     1. EAPCET தேர்வு எழுதுங்கள்
     2. ஆன்லைன் விண்ணப்பம்...
```

## API Reference

### POST `/api/chat`

**Request:**
```json
{
  "message": "CSE cutoff",
  "session_id": "s_abc123",
  "language": "en"  // optional
}
```

**Response:**
```json
{
  "reply": "The cutoff for CSE...",
  "intent": "cutoff",
  "session_id": "s_abc123",
  "sources": ["VNRVJIET Cutoff Database"],
  "language": "en"
}
```

### POST `/api/clear-session`

Clears all session data including language preference:

**Request:**
```json
{
  "session_id": "s_abc123"
}
```

**Response:**
```json
{
  "status": "ok",
  "session_id": "s_abc123",
  "cleared": ["history", "language", "cutoff_data"]
}
```

## Adding New Languages

To add support for a new language:

### 1. Update `app/utils/languages.py`

Add language to `SUPPORTED_LANGUAGES`:
```python
SUPPORTED_LANGUAGES = {
    # ... existing languages
    "ml": {"name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳"},
}
```

Add translations for all keys in `TRANSLATIONS`:
```python
TRANSLATIONS = {
    "welcome_title": {
        # ... existing translations
        "ml": "നമസ്കാരം! 👋 VNRVJIET സഹായിയിലേക്ക് സ്വാഗതം.",
    },
    # ... repeat for all translation keys
}
```

Add language detection pattern:
```python
language_patterns = {
    # ... existing patterns
    "ml": r'[\u0D00-\u0D7F]',  # Malayalam character range
}
```

Add language instruction:
```python
def get_language_instruction(language: str) -> str:
    instructions = {
        # ... existing instructions
        "ml": "മലയാളത്തിൽ ഉത്തരം നൽകുക. Respond completely in Malayalam language.",
    }
    return instructions.get(language, instructions["en"])
```

### 2. Update `app/frontend/widget.js`

Add language to `SUPPORTED_LANGUAGES`:
```javascript
const SUPPORTED_LANGUAGES = {
  // ... existing languages
  ml: { name: "Malayalam", native: "മലയാളം", flag: "🇮🇳" },
};
```

Add translations for all UI keys:
```javascript
const TRANSLATIONS = {
  welcome_title: {
    // ... existing translations
    ml: "നമസ്കാരം! 👋 VNRVJIET സഹായിയിലേക്ക് സ്വാഗതം.",
  },
  // ... repeat for all translation keys
};
```

### 3. Test the New Language

1. Restart the backend server
2. Clear browser cache and session storage
3. Open the chatbot
4. Select the new language
5. Test conversations and UI elements
6. Verify auto-detection works correctly

## Best Practices

### For Developers

1. **Always use translation keys**: Never hardcode text in English
   ```javascript
   // ❌ Bad
   addBotMessage("Welcome to VNRVJIET");
   
   // ✅ Good
   addBotMessage(t("welcome_title"));
   ```

2. **Keep technical terms in English**: Branch names, numbers, etc.
   ```
   Hindi: CSE के लिए कटऑफ रैंक **4,367** है।
   (CSE and the rank number remain in English/numbers)
   ```

3. **Test with all languages**: Ensure new features work across all languages

4. **Preserve language context**: Don't switch language mid-flow unless user requests

### For Content Writers

1. **Be concise**: Translations should match the tone and length of English text
2. **Use formal language**: The chatbot represents an educational institution
3. **Avoid idioms**: Use clear, direct language that translates well
4. **Test readability**: Ensure translations are natural and easy to understand

## Troubleshooting

### Language not detected properly
- Check character ranges in `detect_language()`
- Add more language-specific keywords
- Verify Unicode encoding is correct

### Translations missing
- Check if key exists in `TRANSLATIONS` dict
- Verify language code is correct
- Add fallback to English if translation not found

### Language switch not working
- Verify `sessionStorage` is enabled
- Check browser console for errors
- Ensure session ID is being maintained

### Bot responding in wrong language
- Check `current_language` value in backend session
- Verify language instruction is being added to system prompt
- Check if language parameter is being sent in API request

## Performance Considerations

- Language detection is fast (~1ms) using regex patterns
- Translations are stored in memory (no database lookups required)
- Session storage is browser-local (no server round-trips)
- No performance impact on existing English-only users

## Future Enhancements

Planned improvements:

1. **Voice Input**: Support for speech-to-text in multiple languages
2. **RTL Support**: Right-to-left text for languages like Urdu, Arabic
3. **Regional Variants**: Support for different dialects (e.g., Indian Hindi vs. Standard Hindi)
4. **Transliteration**: Allow typing in Roman script for Indian languages
5. **Language Analytics**: Track which languages are most popular
6. **Context-Aware Translation**: Better handling of technical terms and mixed-language content

## Support

For issues or questions about multilingual support:
- Check this documentation first
- Review the code in `app/utils/languages.py`
- Test with different languages
- Report bugs with language code and example input
