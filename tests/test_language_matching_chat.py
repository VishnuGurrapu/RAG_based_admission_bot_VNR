"""Tests for response-language matching and session language memory."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

import app.api.chat as chat_api
from app.classifier.intent_classifier import ClassificationResult, IntentType
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_chat_language_state(monkeypatch):
    chat_api._DOCUMENT_FLOW_STATE_BY_SESSION.clear()
    chat_api._SESSION_LANGUAGE_BY_ID.clear()

    def force_cutoff(_: str) -> ClassificationResult:
        return ClassificationResult(
            intent=IntentType.CUTOFF,
            confidence=1.0,
            reason="forced cutoff for language tests",
        )

    monkeypatch.setattr(chat_api, "classify", force_cutoff)
    yield
    chat_api._DOCUMENT_FLOW_STATE_BY_SESSION.clear()
    chat_api._SESSION_LANGUAGE_BY_ID.clear()


def test_telugu_query_gets_telugu_missing_branch_response():
    response = client.post(
        "/api/chat",
        json={"message": "బ్రాంచ్‌లకు కట్‌ఆఫ్ ర్యాంకులు", "session_id": "lang-te-1", "language": "en"},
    )
    assert response.status_code == 200
    text = response.json()["response"]
    assert "దయచేసి మీరు ఏ శాఖ గురించి అడుగుతున్నారో పేర్కొనండి." in text


def test_english_query_gets_english_missing_branch_response():
    response = client.post(
        "/api/chat",
        json={"message": "cutoff ranks", "session_id": "lang-en-1", "language": "te"},
    )
    assert response.status_code == 200
    text = response.json()["response"]
    assert "Please specify which branch you're asking about." in text


def test_ambiguous_followup_keeps_session_language():
    session_id = "lang-memory-te"
    first = client.post(
        "/api/chat",
        json={"message": "బ్రాంచ్‌లకు కట్‌ఆఫ్ ర్యాంకులు", "session_id": session_id, "language": "en"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={"message": "CSE cutoff", "session_id": session_id, "language": "en"},
    )
    assert second.status_code == 200
    text = second.json()["response"]
    assert "దయచేసి మీ వర్గాన్ని పేర్కొనండి." in text


def test_different_language_followup_without_switch_request_switches_to_new_language():
    session_id = "lang-lock-en"
    first = client.post(
        "/api/chat",
        json={"message": "cutoff ranks", "session_id": session_id, "language": "en"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={"message": "CSE cutoff क्या है?", "session_id": session_id, "language": "en"},
    )
    assert second.status_code == 200
    assert "कृपया अपनी श्रेणी बताएं।" in second.json()["response"]


def test_clear_english_followup_switches_to_english():
    session_id = "lang-memory-switch"
    first = client.post(
        "/api/chat",
        json={"message": "బ్రాంచ్‌లకు కట్‌ఆఫ్ ర్యాంకులు", "session_id": session_id, "language": "en"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={"message": "What is the CSE cutoff rank?", "session_id": session_id, "language": "en"},
    )
    assert second.status_code == 200
    text = second.json()["response"]
    assert "Please specify your category." in text


def test_explicit_language_switch_changes_language():
    session_id = "lang-explicit-switch"
    first = client.post(
        "/api/chat",
        json={"message": "బ్రాంచ్‌లకు కట్‌ఆఫ్ ర్యాంకులు", "session_id": session_id, "language": "en"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={"message": "Please respond in English", "session_id": session_id, "language": "en"},
    )
    assert second.status_code == 200
    assert "Please specify which branch you're asking about." in second.json()["response"]


def test_documents_prompt_localizes_to_telugu():
    response = client.post(
        "/api/chat",
        json={"message": "అవసరమైన పత్రాలు ఏమిటి?", "session_id": "lang-docs-te", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "మీ ప్రోగ్రామ్" in data["response"]
    assert data["options"][0]["label"].startswith("బి.టెక్")
    assert all(not re.search(r"[A-Za-z]", option["label"]) for option in data["options"])
