"""
scripts/generate_verse.py
Closed-Loop Sanskrit Verse Generator & Pingala Meter Repair Engine
Live Endpoint: https://aigaane.in/api/v3/prosody/scan
"""
import os
import sys
import time
import json
import httpx
from google import genai
from google.genai import types
from google.genai.errors import ServerError

API_URL = os.getenv("PROSODY_API_URL", "https://aigaane.in/api/v3/prosody/scan")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

def verify_prosody_tool(text: str, chandas: str = "anustubh", padanta_guru: bool = True) -> dict:
    payload = {
        "text": text,
        "chandas": chandas,
        "padanta_guru": padanta_guru
    }
    with httpx.Client(timeout=15.0) as client:
        res = client.post(API_URL, json=payload, headers={"Content-Type": "application/json; charset=utf-8"})
        res.raise_for_status()
        return res.json()

prosody_tool_declaration = {
    "name": "verify_prosody",
    "description": "Validates Sanskrit verses against Pingala Chhandahsastra metrics.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "text": {
                "type": "STRING",
                "description": "Devanagari verse text (4 padas separated by newlines)."
            },
            "chandas": {"type": "STRING", "description": "Meter (default: anustubh)"},
            "padanta_guru": {"type": "BOOLEAN", "description": "Treat final syllable as Guru."}
        },
        "required": ["text"]
    }
}

SYSTEM_INSTRUCTION = """
You are a classical Sanskrit Mahakavi and metric expert adhering strictly to Pingala Chhandahsastra.
Your goal is to compose an authentic Anuṣṭubh (Pathyā) verse on the user-requested topic.

Meter Rules for Anuṣṭubh Pathyā:
1. Exactly 4 Pādas, each having strictly 8 akṣaras (syllables).
2. Syllable 5 of ALL 4 pādas must be Laghu (L).
3. Syllable 6 of ALL 4 pādas must be Guru (G).
4. Syllable 7 must ALTERNATE:
   - Pāda 1: Guru (G)
   - Pāda 2: Laghu (L)
   - Pāda 3: Guru (G)
   - Pāda 4: Laghu (L)

Workflow:
1. Compose candidate 4-pāda verse in Devanagari.
2. Call `verify_prosody`.
3. If diagnostics show failures, rewrite ONLY the failing pādas to hit the 8-syllable and Laghu/Guru requirements, then re-call `verify_prosody`.
"""

def safe_send(chat, message, retries=5, delay=4):
    for attempt in range(1, retries + 1):
        try:
            return chat.send_message(message)
        except ServerError as e:
            if "503" in str(e) and attempt < retries:
                print(f"[Notice] 503 Server Busy. Retrying in {delay}s (Attempt {attempt}/{retries})...")
                time.sleep(delay)
                delay *= 2
            else:
                raise

def generate_verified_verse(topic: str, max_iterations: int = 5):
    client = genai.Client(api_key=GEMINI_API_KEY)
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            tools=[types.Tool(function_declarations=[prosody_tool_declaration])]
        )
    )

    print(f"\n[Composer] Requesting composition on: '{topic}'")
    response = safe_send(chat, f"Compose an Anustubh Pathya sloka on: {topic}")

    for step in range(1, max_iterations + 1):
        tool_calls = [
            part.function_call
            for cand in response.candidates
            for part in cand.content.parts
            if part.function_call
        ]

        if not tool_calls:
            print("\n[Final Output]:")
            print(response.text)
            return

        for call in tool_calls:
            fn_name = call.name
            args = dict(call.args)
            candidate_text = args.get("text")
            print(f"\n[Iteration {step}] Candidate Verse:\n{candidate_text}")

            result = verify_prosody_tool(
                text=candidate_text,
                chandas=args.get("chandas", "anustubh"),
                padanta_guru=args.get("padanta_guru", True)
            )

            is_valid = result.get("valid", False)
            variant = result.get("variant")
            print(f">> Scansion Result: Valid={is_valid} | Variant={variant}")

            if is_valid:
                print("\n==================================================")
                print("✨ VERIFIED AUTHENTIC ANUṢṬUBH (PATHYĀ) VERSE ✨")
                print("==================================================")
                print(candidate_text.strip())
                print("--------------------------------------------------")
                for p in result.get("padas", []):
                    cadence = p["weight_pattern"][4:7]
                    print(f"Pāda {p['pada_number']}: {p['text']} -> {p['weight_pattern']} (Cadence 5-7: {cadence})")
                print("Authority: Piṅgala Chhandaḥśāstra | Governance: Passed")
                print("==================================================\n")
                return

            diags = result.get("diagnostics", [])
            print(f">> Defects caught: {len(diags)}")
            for d in diags:
                print(f"   - Pada {d['pada']}, Syl {d['syllable']}: {d['message']}")

            response = safe_send(
                chat,
                types.Part.from_function_response(name=fn_name, response={"result": result})
            )

if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "प्रज्ञा (Wisdom and Truth)"
    generate_verified_verse(theme)
