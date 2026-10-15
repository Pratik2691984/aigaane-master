"""
tests/test_repair_loop.py
Automated Unit Tests for Closed-Loop Agentic Verse Repair, Exhaustion, and Transport Exceptions
Exercises the real generate_verified_verse driver function using mocked LLM transport and verifier.
"""
import pytest
from unittest.mock import MagicMock, patch
from scripts.generate_verse import generate_verified_verse, RepairLoopExhausted, RepairLoopTransportError

class MockPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call

class MockCandidate:
    def __init__(self, parts):
        self.content = MagicMock(parts=parts)

class MockResponse:
    def __init__(self, candidates, text=""):
        self.candidates = candidates
        self.text = text

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

@patch("scripts.generate_verse.verify_prosody_tool")
@patch("scripts.generate_verse.genai.Client")
def test_repair_loop_real_convergence(mock_genai_client, mock_verify):
    broken_verse = "प्रज्ञा प्रदीपेन तमोविनाशम्\nमोहान्धकारं सहसा निहन्ति।\nकरोति चेतः सुविशुद्धमेव\nसत्यं परं दर्शयति प्रकामम्॥"
    valid_verse = "प्रज्ञा तमोघ्नी च तमोनुती च\nदीप्तेव शुद्धा मनसोऽभिवृत्तिः ।\nसंसारसिन्धोस्तरणीयशेषा\nविज्ञानदृष्टिः परमा हि विद्या ॥"

    fc = MockFunctionCall("verify_prosody", {"text": broken_verse, "chandas": "upajati", "padanta_guru": True})
    resp1 = MockResponse([MockCandidate([MockPart(function_call=fc)])])
    resp2 = MockResponse([], text=valid_verse)

    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = [resp1, resp2]
    mock_genai_client.return_value.chats.create.return_value = mock_chat

    mock_verify.side_effect = [
        {
            "valid": False,
            "chandas": "indravajrā",
            "diagnostics": [{"pada": 1, "syllable": 9, "message": "Pāda 1 has 9 akṣaras, expected 11."}]
        },
        {
            "valid": True,
            "chandas": "indravajrā",
            "variant": "śuddha",
            "padas": [{"pada_number": 1, "text": valid_verse.splitlines()[0], "weight_pattern": "GGLGGLLGLGG", "total_syllables": 11}]
        }
    ]

    result = generate_verified_verse(topic="प्रज्ञा", meter="upajati", max_iterations=3)

    assert mock_verify.call_count == 2
    assert mock_chat.send_message.call_count == 2
    assert result["valid"] is True
    assert result["iterations"] == 2

@patch("scripts.generate_verse.verify_prosody_tool")
@patch("scripts.generate_verse.genai.Client")
def test_repair_loop_terminates_on_exhaustion(mock_genai_client, mock_verify):
    broken_verse = "प्रज्ञा प्रदीपेन तमोविनाशम्..."
    fc = MockFunctionCall("verify_prosody", {"text": broken_verse, "chandas": "anustubh"})
    resp = MockResponse([MockCandidate([MockPart(function_call=fc)])])

    mock_chat = MagicMock()
    mock_chat.send_message.return_value = resp
    mock_genai_client.return_value.chats.create.return_value = mock_chat

    mock_verify.return_value = {
        "valid": False,
        "chandas": "anuṣṭubh",
        "diagnostics": [{"pada": 1, "syllable": 5, "message": "Expected Laghu."}]
    }

    with pytest.raises(RepairLoopExhausted) as exc_info:
        generate_verified_verse(topic="प्रज्ञा", meter="anustubh", max_iterations=2)

    assert exc_info.value.iterations == 2
    assert len(exc_info.value.last_diagnostics) == 1
    assert mock_verify.call_count == 2

@patch("scripts.generate_verse.verify_prosody_tool")
@patch("scripts.generate_verse.genai.Client")
def test_repair_loop_wraps_transport_timeout(mock_genai_client, mock_verify):
    """Asserts that mid-loop transport timeouts are wrapped into typed RepairLoopTransportError."""
    broken_verse = "प्रज्ञा प्रदीपेन तमोविनाशम्..."
    fc = MockFunctionCall("verify_prosody", {"text": broken_verse, "chandas": "anustubh"})
    resp = MockResponse([MockCandidate([MockPart(function_call=fc)])])

    mock_chat = MagicMock()
    # First message succeeds to enter loop, second (safe_send during repair) times out
    mock_chat.send_message.side_effect = [resp, TimeoutError("Exceeded safe retry limit")]
    mock_genai_client.return_value.chats.create.return_value = mock_chat

    mock_verify.return_value = {
        "valid": False,
        "chandas": "anuṣṭubh",
        "diagnostics": [{"pada": 1, "syllable": 5, "message": "Expected Laghu."}]
    }

    with pytest.raises(RepairLoopTransportError) as exc_info:
        generate_verified_verse(topic="प्रज्ञा", meter="anustubh", max_iterations=3)

    assert exc_info.value.iterations == 1
    assert isinstance(exc_info.value.cause, TimeoutError)
