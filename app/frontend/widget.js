/**
 * VNRVJIET Admissions Chatbot – Widget JavaScript
 * =================================================
 * Handles: toggle, send/receive, typing indicator,
 *          session management, markdown rendering,
 *          quick replies, timestamps.
 */

(function () {
  "use strict";

  // ── Configuration ────────────────────────────────────────────
  const API_BASE = window.CHATBOT_API_BASE || "";
  const COLLEGE = "VNRVJIET";

  // ── DOM References ───────────────────────────────────────────
  const toggleBtn = document.getElementById("chat-toggle");
  const container = document.getElementById("chat-container");
  const closeBtn = document.getElementById("chat-close");
  const homeBtn = document.getElementById("home-btn");
  const messagesEl = document.getElementById("chat-messages");
  const inputEl = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  const inputArea = document.getElementById("chat-input-area");
  const welcomePopup = document.getElementById("welcome-popup");
  const popupClose = document.getElementById("popup-close");
  let typingEl = null;

  // ── State ────────────────────────────────────────────────────
  let isOpen = false;
  let isSending = false;
  let sessionId = sessionStorage.getItem("chatbot_session") || generateId();
  sessionStorage.setItem("chatbot_session", sessionId);
  
  // Language preference - check if user has explicitly selected a language
  let currentLanguage = sessionStorage.getItem("chatbot_language") || "en";
  let languageSelected = sessionStorage.getItem("chatbot_language_selected") === "true";
  
  // Debug logging
  console.log("Chatbot initialized:", {
    sessionId,
    currentLanguage,
    languageSelected,
    version: "v20-multilingual"
  });
  
  // Chat history is preserved in this session for context-aware responses
  // The backend automatically uses conversation history for better answers

  // ── Language Support ─────────────────────────────────────────
  const SUPPORTED_LANGUAGES = {
    en: { name: "English", native: "English", flag: "🇬🇧" },
    hi: { name: "Hindi", native: "हिन्दी", flag: "🇮🇳" },
    te: { name: "Telugu", native: "తెలుగు", flag: "🇮🇳" },
    ta: { name: "Tamil", native: "தமிழ்", flag: "🇮🇳" },
    mr: { name: "Marathi", native: "मराठी", flag: "🇮🇳" },
    kn: { name: "Kannada", native: "ಕನ್ನಡ", flag: "🇮🇳" },
  };

  const TRANSLATIONS = {
    welcome_title: {
      en: "Hello! 👋 Welcome to the **VNRVJIET** assistant.",
      hi: "नमस्ते! 👋 **VNRVJIET** सहायक में आपका स्वागत है।",
      te: "నమస్కారం! 👋 **VNRVJIET** సహాయకునికి స్వాగతం।",
      ta: "வணக்கம்! 👋 **VNRVJIET** உதவியாளருக்கு வரவேற்கிறோம்.",
      mr: "नमस्कार! 👋 **VNRVJIET** सहाय्यकांमध्ये आपले स्वागत आहे.",
      kn: "ನಮಸ್ಕಾರ! 👋 **VNRVJIET** ಸಹಾಯಕನಿಗೆ ಸ್ವಾಗತ.",
    },
    welcome_select_topic: {
      en: "I can help you with the following topics. Please select one:",
      hi: "मैं निम्नलिखित विषयों में आपकी मदद कर सकता/सकती हूं। कृपया एक चुनें:",
      te: "నేను ఈ క్రింది అంశాలలో మీకు సహాయం చేయగలను. దయచేసి ఒకదాన్ని ఎంచుకోండి:",
      ta: "நான் பின்வரும் தலைப்புகளில் உங்களுக்கு உதவ முடியும். தயவுசெய்து ஒன்றைத் தேர்ந்தெடுக்கவும்:",
      mr: "मी खालील विषयांमध्ये तुमची मदत करू शकतो. कृपया एक निवडा:",
      kn: "ನಾನು ಈ ಕೆಳಗಿನ ವಿಷಯಗಳಲ್ಲಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು. ದಯವಿಟ್ಟು ಒಂದನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
    },
    language_prompt: {
      en: "Please select your preferred language:",
      hi: "कृपया अपनी पसंदीदा भाषा चुनें:",
      te: "దయచేసి మీ ఇష్ట భాషను ఎంచుకోండి:",
      ta: "உங்களுக்கு விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்:",
      mr: "कृपया तुमची पसंतीची भाषा निवडा:",
      kn: "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
    },
    category_admission: {
      en: "Admission Process & Eligibility",
      hi: "प्रवेश प्रक्रिया और पात्रता",
      te: "ప్రవేశ ప్రక్రియ & అర్హత",
      ta: "சேர்க்கை செயல்முறை & தகுதி",
      mr: "प्रवेश प्रक्रिया आणि पात्रता",
      kn: "ಪ್ರವೇಶ ಪ್ರಕ್ರಿಯೆ ಮತ್ತು ಅರ್ಹತೆ",
    },
    category_cutoff: {
      en: "Branch-wise Cutoff Ranks",
      hi: "शाखा-वार कटऑफ रैंक",
      te: "బ్రాంచ్-వారీ కటాఫ్ ర్యాంక్‌లు",
      ta: "கிளை வாரியான கட்ஆஃப் தரவரிசை",
      mr: "शाखा-निहाय कटऑफ रॅंक",
      kn: "ಶಾಖೆಯ ಪ್ರಕಾರ ಕಟ್‌ಆಫ್ ಶ್ರೇಣಿಗಳು",
    },
    category_documents: {
      en: "Required Documents",
      hi: "आवश्यक दस्तावेज",
      te: "అవసరమైన పత్రాలు",
      ta: "தேவையான ஆவணங்கள்",
      mr: "आवश्यक कागदपत्रे",
      kn: "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
    },
    category_fees: {
      en: "Fee Structure & Scholarships",
      hi: "शुल्क संरचना और छात्रवृत्ति",
      te: "ఫీజు నిర్మాణం & స్కాలర్‌షిప్‌లు",
      ta: "கட்டணம் & உதவித்தொகை",
      mr: "फी रचना आणि शिष्यवृत्ती",
      kn: "ಶುಲ್ಕ ರಚನೆ ಮತ್ತು ವಿದ್ಯಾರ್ಥಿವೇತನ",
    },
    category_others: {
      en: "Others",
      hi: "अन्य",
      te: "ఇతరములు",
      ta: "மற்றவை",
      mr: "इतर",
      kn: "ಇತರೆ",
    },
    input_placeholder: {
      en: "Ask about admissions...",
      hi: "प्रवेश के बारे में पूछें...",
      te: "ప్రవేశాల గురించి అడగండి...",
      ta: "சேர்க்கை பற்றி கேளுங்கள்...",
      mr: "प्रवेशाबद्दल विचारा...",
      kn: "ಪ್ರವೇಶದ ಬಗ್ಗೆ ಕೇಳಿ...",
    },
    error_connection: {
      en: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
      hi: "क्षमा करें, मुझे अभी कनेक्ट करने में समस्या हो रही है। कृपया कुछ देर बाद पुनः प्रयास करें।",
      te: "క్షమించండి, నాకు ఇప్పుడు కనెక్ట్ చేయడంలో సమస్య ఉంది. దయచేసి కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి।",
      ta: "மன்னிக்கவும், இப்போது இணைப்பதில் சிக்கல் உள்ளது. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.",
      mr: "क्षमस्व, मला आत्ता कनेक्ट होण्यात समस्या येत आहे. कृपया काही वेळाने पुन्हा प्रयत्न करा.",
      kn: "ಕ್ಷಮಿಸಿ, ನನಗೆ ಈಗ ಸಂಪರ್ಕ ಸಾಧಿಸುವಲ್ಲಿ ತೊಂದರೆ ಇದೆ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    },
    rate_limit: {
      en: "You're sending messages too quickly. Please wait a moment and try again.",
      hi: "आप बहुत जल्दी संदेश भेज रहे हैं। कृपया प्रतीक्षा करें और पुनः प्रयास करें।",
      te: "మీరు చాలా త్వరగా సందేశాలు పంపుతున్నారు. దయచేసి కాసేపు వేచి ఉండి మళ్లీ ప్రయత్నించండి।",
      ta: "நீங்கள் மிக விரைவாக செய்திகளை அனுப்புகிறீர்கள். சிறிது நேரம் காத்திருந்து மீண்டும் முயற்சிக்கவும்.",
      mr: "तुम्ही खूप वेगाने संदेश पाठवत आहात. कृपया थांबा आणि पुन्हा प्रयत्न करा.",
      kn: "ನೀವು ತುಂಬಾ ವೇಗವಾಗಿ ಸಂದೇಶಗಳನ್ನು ಕಳುಹಿಸುತ್ತಿದ್ದೀರಿ. ದಯವಿಟ್ಟು ಕಾಯಿರಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    },
    change_language: {
      en: "🌐 Change Language",
      hi: "🌐 भाषा बदलें",
      te: "🌐 భాష మార్చండి",
      ta: "🌐 மொழியை மாற்றவும்",
      mr: "🌐 भाषा बदला",
      kn: "🌐 ಭಾಷೆಯನ್ನು ಬದಲಿಸಿ",
    },
  };

  function t(key) {
    return TRANSLATIONS[key]?.[currentLanguage] || TRANSLATIONS[key]?.en || key;
  }

  function setLanguage(lang) {
    console.log("Setting language to:", lang);
    if (SUPPORTED_LANGUAGES[lang]) {
      currentLanguage = lang;
      sessionStorage.setItem("chatbot_language", lang);
      sessionStorage.setItem("chatbot_language_selected", "true");
      languageSelected = true;
      
      // Update input placeholder
      if (inputEl) {
        inputEl.placeholder = t("input_placeholder");
      }
      
      console.log("Language set successfully:", lang);
    } else {
      console.error("Unsupported language:", lang);
    }
  }
  
  // Chat history is preserved in this session for context-aware responses
  // The backend automatically uses conversation history for better answers

  // ── Helpers ──────────────────────────────────────────────────
  function generateId() {
    return "s_" + Math.random().toString(36).substring(2, 10);
  }

  function timestamp() {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  /** Minimal Markdown → HTML (headings, bold, italic, lists, line breaks) */
  function renderMarkdown(text) {
    let html = text
      // Headings: ### h3, ## h2, # h1 (must be at line start)
      .replace(/^###\s+(.+)$/gm, "<strong style='font-size:1.05em;display:block;margin:8px 0 4px;'>$1</strong>")
      .replace(/^##\s+(.+)$/gm, "<strong style='font-size:1.1em;display:block;margin:8px 0 4px;'>$1</strong>")
      .replace(/^#\s+(.+)$/gm, "<strong style='font-size:1.15em;display:block;margin:8px 0 4px;'>$1</strong>")
      // Bold **text**
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      // Italic *text*
      .replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, "<em>$1</em>")
      // Inline code `text`
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      // Unordered list items
      .replace(/^[\s]*[-•]\s+(.+)$/gm, "<li>$1</li>")
      // Ordered list items
      .replace(/^[\s]*\d+\.\s+(.+)$/gm, "<li>$1</li>")
      // Line breaks
      .replace(/\n/g, "<br>");

    // Wrap consecutive <li> in <ul>
    html = html.replace(
      /(<li>.*?<\/li>(?:<br>)?)+/g,
      (match) => "<ul>" + match.replace(/<br>/g, "") + "</ul>"
    );

    return html;
  }

  // ── UI Functions ─────────────────────────────────────────────

  function toggleChat() {
    isOpen = !isOpen;
    container.classList.toggle("visible", isOpen);
    toggleBtn.classList.toggle("open", isOpen);

    if (isOpen) {
      // Show welcome if first time
      if (messagesEl.children.length === 0) {
        showWelcome();
      }
      // Only focus input if it's visible
      if (inputArea.style.display !== "none") {
        inputEl.focus();
      }
    }
  }

  /** Open chat without toggling (for auto-popup) */
  function openChat() {
    if (!isOpen) {
      isOpen = true;
      container.classList.add("visible");
      toggleBtn.classList.add("open");
    }
  }

  /** Close chat */
  function closeChat() {
    if (isOpen) {
      isOpen = false;
      container.classList.remove("visible");
      toggleBtn.classList.remove("open");
    }
  }

  // ── Category definitions with follow-up questions ──────────
  // Category names will be translated dynamically
  const CATEGORY_KEYS = {
    "admission": "category_admission",
    "cutoff": "category_cutoff",
    "documents": "category_documents",
    "fees": "category_fees",
    "others": "category_others",
  };
  
  const CATEGORIES_EN = {
    "Admission Process & Eligibility": [
      "What is the admission process?",
      "Am I eligible for admission?",
      "What exams are accepted?",
      "What is the selection criteria?",
    ],
    "Branch-wise Cutoff Ranks": [
      "Show cutoff trend analysis for a branch",
      "CSE cutoff for OC category?",
      "ECE cutoff for BC-B category?",
      "What was last year's closing rank?",
      "Cutoff for management quota?",
    ],
    "Required Documents": [
      "Documents required for admission?",
      "Is migration certificate needed?",
      "Documents for fee payment?",
      "What ID proofs are required?",
    ],
    "Fee Structure & Scholarships": [
      "What is the fee structure?",
      "Are there any scholarships?",
      "Is fee payment in installments?",
      "Scholarship for SC/ST students?",
    ],
    "Others": [
      "Hostel & accommodation details?",
      "Placement & internship info?",
      "Campus facilities & labs?",
      "NRI / Management quota process?",
      "Talk to admission department",
    ],
  };
  
  function getTranslatedCategories() {
    return [
      t("category_admission"),
      t("category_cutoff"),
      t("category_documents"),
      t("category_fees"),
    ];
  }

  function showWelcome() {
    console.log("showWelcome called, languageSelected:", languageSelected);
    
    // Show language selector if not yet selected
    if (!languageSelected) {
      console.log("Showing language selector");
      showLanguageSelector();
      return;
    }
    
    console.log("Showing welcome in language:", currentLanguage);
    addBotMessage(
      t("welcome_title") + "\n\n" + t("welcome_select_topic")
    );

    // Show category buttons + Others
    addCategoryButtons();
    
    // Add language change button at the bottom
    addLanguageChangeButton();
    
    // Hide input area when showing welcome buttons
    inputArea.style.display = "none";
  }

  /** Show language selector on first interaction */
  function showLanguageSelector() {
    console.log("showLanguageSelector called");
    addBotMessage(t("language_prompt"));
    
    // Hide input area when showing language selector
    inputArea.style.display = "none";
    
    const wrapper = document.createElement("div");
    wrapper.className = "message bot";

    const grid = document.createElement("div");
    grid.className = "language-buttons";
    grid.style.cssText = "display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; max-width: 300px;";

    Object.entries(SUPPORTED_LANGUAGES).forEach(([code, info]) => {
      const btn = document.createElement("button");
      btn.className = "language-btn";
      btn.style.cssText = (
        "padding: 12px; border: 2px solid #e0e0e0; background: white; " +
        "border-radius: 8px; cursor: pointer; transition: all 0.2s; " +
        "font-size: 14px; display: flex; align-items: center; gap: 8px; " +
        "justify-content: center;"
      );
      btn.innerHTML = `<span style="font-size: 20px;">${info.flag}</span><span style="font-weight: 500;">${info.native}</span>`;
      
      btn.addEventListener("mouseover", () => {
        btn.style.borderColor = "#1976d2";
        btn.style.backgroundColor = "#f0f7ff";
      });
      btn.addEventListener("mouseout", () => {
        btn.style.borderColor = "#e0e0e0";
        btn.style.backgroundColor = "white";
      });
      
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        console.log("Language selected:", code, info.native);
        wrapper.remove();
        setLanguage(code);
        addUserMessage(info.native);
        showWelcome();  // Show welcome in selected language
        // Keep input visible for continuous interaction
        showInputArea();
      });
      grid.appendChild(btn);
    });

    wrapper.appendChild(grid);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
    
    console.log("Language selector displayed with", Object.keys(SUPPORTED_LANGUAGES).length, "languages");
  }

  /** Add language change button to allow users to switch language */
  function addLanguageChangeButton() {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot";
    wrapper.style.marginTop = "10px";

    const btn = document.createElement("button");
    btn.className = "language-change-btn";
    btn.textContent = t("change_language");
    btn.style.cssText = (
      "padding: 8px 16px; background: #f5f5f5; border: 1px solid #ddd; " +
      "border-radius: 20px; cursor: pointer; font-size: 12px; " +
      "color: #555; transition: all 0.2s;"
    );
    
    btn.addEventListener("mouseover", () => {
      btn.style.backgroundColor = "#e0e0e0";
    });
    btn.addEventListener("mouseout", () => {
      btn.style.backgroundColor = "#f5f5f5";
    });
    
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      languageSelected = false;  // Reset language selection
      sessionStorage.removeItem("chatbot_language_selected");
      messagesEl.innerHTML = "";  // Clear messages
      showWelcome();  // This will show language selector
    });

    wrapper.appendChild(btn);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
  }

  /** Return to home screen while preserving chat history */
  function returnToHome() {
    // Clear visual messages
    messagesEl.innerHTML = "";
    
    // Hide input area
    inputArea.style.display = "none";
    inputEl.value = "";
    
    // Keep the same session ID to preserve chat history
    // This allows the model to use previous conversation context
    
    // Show welcome screen
    showWelcome();
  }

  /** Render main category buttons + "Others" */
  function addCategoryButtons() {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot";

    const grid = document.createElement("div");
    grid.className = "category-buttons";

    const icons = [
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/></svg>',
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>',
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 6v2m0 8v2"/></svg>',
    ];
    
    const translatedCategories = getTranslatedCategories();
    const categoriesEnKeys = Object.keys(CATEGORIES_EN).filter(c => c !== "Others");

    translatedCategories.forEach((cat, i) => {
      const btn = document.createElement("button");
      btn.className = "category-btn";
      btn.innerHTML = `<span class="cat-icon">${icons[i]}</span><span class="cat-label">${cat}</span>`;
      
      const enKey = categoriesEnKeys[i];  // Get corresponding English key
      
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        wrapper.remove();
        addUserMessage(cat);
        // Send the query (skip adding user message since we already added it above)
        sendMessage(cat, true);
      });
      grid.appendChild(btn);
    });

    // "Others" button
    const othersBtn = document.createElement("button");
    othersBtn.className = "category-btn others-btn";
    const othersText = t("category_others");
    othersBtn.innerHTML = `<span class="cat-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg></span><span class="cat-label">${othersText}</span>`;
    othersBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      wrapper.remove();
      // Don't add user message here - just show input area
      // User will type their own question
      showInputArea();
      inputEl.focus();
      // Optionally show a prompt
      if (currentLanguage !== "en") {
        addBotMessage("Please type your question:");
      }
    });
    grid.appendChild(othersBtn);

    wrapper.appendChild(grid);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
  }

  /** Render follow-up question buttons for a category */
  function addFollowUpButtons(questions, category) {
    // Simplified - just show input for multilingual support
    // Backend will handle the conversation in user's language
    showInputArea();
  }

  function addMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    if (sender === "bot") {
      bubble.innerHTML = renderMarkdown(text);
    } else {
      bubble.textContent = text;
    }

    const ts = document.createElement("span");
    ts.className = "timestamp";
    ts.textContent = timestamp();
    bubble.appendChild(ts);

    msgDiv.appendChild(bubble);
    messagesEl.appendChild(msgDiv);
    scrollToBottom();
  }

  function addBotMessage(text) {
    addMessage(text, "bot");
    // Always show and enable input area after bot message
    // This ensures users can type their answers during conversation flows
    showInputArea();
    inputEl.disabled = false;
    sendBtn.disabled = false;
  }

  function addUserMessage(text) {
    addMessage(text, "user");
  }

  function addQuickReplies(options) {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot";

    const qr = document.createElement("div");
    qr.className = "quick-replies";

    options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.textContent = opt;
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        wrapper.remove(); // remove chips after click
        sendMessage(opt);
      });
      qr.appendChild(btn);
    });

    wrapper.appendChild(qr);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
  }

  function showTyping() {
    if (typingEl) return; // already showing
    typingEl = document.createElement("div");
    typingEl.id = "typing-indicator";
    typingEl.className = "typing-indicator active";
    typingEl.innerHTML =
      '<div class="bubble"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
    messagesEl.appendChild(typingEl);
    scrollToBottom();
  }

  function hideTyping() {
    if (typingEl) {
      typingEl.remove();
      typingEl = null;
    }
  }

  /** Show the input area (hidden until user picks a category) */
  function showInputArea() {
    inputArea.style.display = "";
    // Focus on input field when shown (if chat is open)
    if (isOpen) {
      setTimeout(() => inputEl.focus(), 100);
    }
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  // ── Auto-Popup Welcome Messages ──────────────────────────────

  /**
   * Display welcome popup bubble next to chatbot icon
   * Triggers only once per session
   */
  async function showAutoWelcomeMessages() {
    const POPUP_SHOWN_KEY = "chatbot_popup_shown";
    
    // Check if popup was already shown in this session
    if (sessionStorage.getItem(POPUP_SHOWN_KEY)) {
      return;
    }

    // Mark as shown for this session
    sessionStorage.setItem(POPUP_SHOWN_KEY, "true");

    // Wait 5 seconds after page load before showing welcome popup
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Show the popup bubble
    showWelcomePopup();

    // Auto-hide popup after 5 seconds if no interaction
    setTimeout(() => {
      hideWelcomePopup();
    }, 5000);
  }

  /**
   * Show the welcome popup bubble
   */
  function showWelcomePopup() {
    if (welcomePopup) {
      welcomePopup.style.display = '';
      welcomePopup.classList.add('visible');
    }
  }

  /**
   * Hide the welcome popup bubble
   */
  function hideWelcomePopup() {
    if (welcomePopup) {
      welcomePopup.classList.remove('visible');
      // Force hide with inline style as fallback
      setTimeout(() => {
        if (welcomePopup && !welcomePopup.classList.contains('visible')) {
          welcomePopup.style.display = 'none';
        }
      }, 400);
    }
  }

  /**
   * Open chat from popup - shows welcome screen
   */
  function openChatFromPopup() {
    // Hide the popup
    hideWelcomePopup();
    
    // Open the chat
    openChat();
    
    // Show welcome if first time or no messages
    if (messagesEl.children.length === 0) {
      showWelcome();
    }
  }

  // ── API Communication ────────────────────────────────────────

  async function sendMessage(text, skipAddingUserMessage = false) {
    if (!text || !text.trim() || isSending) return;

    const userText = text.trim();
    
    // Only add user message if not already added (prevents duplicates)
    if (!skipAddingUserMessage) {
      addUserMessage(userText);
    }
    
    inputEl.value = "";
    inputEl.disabled = true;
    sendBtn.disabled = true;
    isSending = true;

    showTyping();

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          session_id: sessionId,
          language: currentLanguage,
        }),
      });

      if (response.status === 429) {
        hideTyping();
        addBotMessage(t("rate_limit"));
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      hideTyping();

      sessionId = data.session_id || sessionId;
      sessionStorage.setItem("chatbot_session", sessionId);
      
      // Update language if backend changed it
      if (data.language && data.language !== currentLanguage) {
        setLanguage(data.language);
      }

      addBotMessage(data.reply);

      // Source citations
      if (data.sources && data.sources.length > 0) {
        const srcText =
          "📄 *Sources: " + data.sources.join(", ") + "*";
        // Small muted source line (append to last bot bubble)
        const bubbles = messagesEl.querySelectorAll(".message.bot .bubble");
        if (bubbles.length > 0) {
          const last = bubbles[bubbles.length - 1];
          const srcSpan = document.createElement("div");
          srcSpan.style.cssText =
            "font-size:10px;color:#888;margin-top:6px;font-style:italic;";
          srcSpan.textContent = "📄 Sources: " + data.sources.join(", ");
          last.appendChild(srcSpan);
        }
      }
    } catch (err) {
      hideTyping();
      console.error("Chat error:", err);
      addBotMessage(t("error_connection"));
    } finally {
      isSending = false;
      inputEl.disabled = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }



  // ── Event Listeners ──────────────────────────────────────────

  toggleBtn.addEventListener("click", toggleChat);
  closeBtn.addEventListener("click", toggleChat);

  // Close popup button - simple and direct
  if (popupClose) {
    popupClose.onclick = function(e) {
      e.stopPropagation();
      hideWelcomePopup();
    };
  }

  // Popup message click to open chat
  if (welcomePopup) {
    const popupMessage = welcomePopup.querySelector('.popup-message');
    if (popupMessage) {
      popupMessage.onclick = function(e) {
        // Don't trigger if clicking close button
        if (e.target.id === 'popup-close' || e.target.closest('#popup-close')) {
          return;
        }
        openChatFromPopup();
      };
    }
  }
  
  homeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    returnToHome();
  });

  sendBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    sendMessage(inputEl.value);
  });

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputEl.value);
    }
  });

  // Close widget when clicking outside (improved to prevent accidental closures)
  document.addEventListener("click", (e) => {
    if (!isOpen) return;
    
    // Check if click is outside both the container and toggle button
    const clickedInsideContainer = container.contains(e.target);
    const clickedToggleBtn = toggleBtn.contains(e.target);
    const clickedInsidePopup = welcomePopup && welcomePopup.contains(e.target);
    
    // Only close if click is truly outside all chat-related elements
    if (!clickedInsideContainer && !clickedToggleBtn && !clickedInsidePopup) {
      isOpen = false;
      container.classList.remove("visible");
      toggleBtn.classList.remove("open");
    }
  });

  // ── Accessibility ────────────────────────────────────────────
  toggleBtn.setAttribute("aria-label", "Open chat");
  closeBtn.setAttribute("aria-label", "Close chat");

  // ── Auto-Popup on Page Load ──────────────────────────────────
  // Trigger auto-welcome messages after page loads
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showAutoWelcomeMessages);
  } else {
    // DOM already loaded
    showAutoWelcomeMessages();
  }
})();
