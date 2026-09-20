"""
scripts/generate_verse.py
Multi-Meter Closed-Loop Sanskrit Verse Generator & Repair Engine
Supports: Anuṣṭubh (Pathyā) & Upajāti (Indravajrā / Upendravajrā)
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
            "chandas": {
                "type": "STRING", 
                "description": "Target meter: 'anustubh' or 'upajati' (covers indravajra/upendravajra)."
            },
            "padanta_guru": {
                "type": "BOOLEAN", 
                "description": "Treat final syllable as Guru (padanta-laghu-guru rule)."
            }
        },
        "required": ["text", "chandas"]
    }
}

SYSTEM_INSTRUCTION_ANUSTUBH = """
You are a classical Sanskrit Mahākavi adhering strictly to Piṅgala Chhandaḥśāstra.
Compose an authentic 4-pāda Anuṣṭubh (Pathyā) verse on the given topic.
Rules:
1. Strictly 4 pādas, each having exactly 8 akṣaras.
2. Syllable 5 = L (Laghu) across all pādas.
3. Syllable 6 = G (Guru) across all pādas.
4. Syllable 7 alternates: Pāda 1=G, Pāda 2=L, Pāda 3=G, Pāda 4=L.
Call verify_prosody(text, chandas='anustubh'). If defects are returned, repair only the faulty pādas and call again.
"""

SYSTEM_INSTRUCTION_UPAJATI = """
You are a classical Sanskrit Mahākavi adhering strictly to Piṅgala Chhandaḥśāstra.
Compose an authentic 4-pāda Upajāti / Indravajrā verse on the given topic.
Rules:
1. Exactly 4 pādas, each having strictly 11 akṣaras.
2. Each pāda must strictly follow either:
   - Indravajrā (Ta-Ta-Ja-G-G): GGLGGLLGLGG
   - Upendravajrā (Ja-Ta-Ja-G-G): LGLGGLLGLGG
3. Pāda 1 Syllable 1 can be Guru (Indravajrā) or Laghu (Upendravajrā). Syllables 2-11 are identical in both meters.
Call verify_prosody(text, chandas='upajati'). If defects are returned, adjust words to fix the syllable weights and call again.
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

def generate_verified_verse(topic: str, meter: str = "anustubh", max_iterations: int = 5):
    system_prompt = SYSTEM_INSTRUCTION_UPAJATI if meter.lower() in ["upajati", "indravajra"] else SYSTEM_INSTRUCTION_ANUSTUBH
    target_meter = "upajati" if meter.lower() in ["upajati", "indravajra"] else "anustubh"

    client = genai.Client(api_key=GEMINI_API_KEY)
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            tools=[types.Tool(function_declarations=[prosody_tool_declaration])]
        )
    )

    print(f"\n[Composer] Requesting '{target_meter}' verse on: '{topic}'")
    response = safe_send(chat, f"Compose a 4-pada Sanskrit sloka in {target_meter} meter on the topic: {topic}")

    for step in range(1, max_iterations + 1):
        tool_calls = [
            part.function_call
            for cand in response.candidates
            for part in cand.content.parts
            if part.function_call
        ]

        if not tool_calls:
            print("\n[Final Text Output]:\n", response.text)
            return

        for call in tool_calls:
            fn_name = call.name
            args = dict(call.args)
            candidate_text = args.get("text", "")
            scanned_chandas = args.get("chandas", target_meter)
            print(f"\n[Iteration {step}] Candidate Verse:\n{candidate_text}")

            result = verify_prosody_tool(
                text=candidate_text,
                chandas=scanned_chandas,
                padanta_guru=args.get("padanta_guru", True)
            )

            is_valid = result.get("valid", False)
            print(f">> Result: Valid={is_valid} | Chandas={result.get('chandas')} | Variant={result.get('variant')}")

            if is_valid:
                print("\n" + "="*54)
                print(f"✨ VERIFIED AUTHENTIC {result.get('chandas', target_meter).upper()} VERSE ✨")
                print("="*54)
                print(candidate_text.strip())
                print("-" * 54)
                for p in result.get("padas", []):
                    print(f"Pāda {p['pada_number']}: {p['text']} -> {p['weight_pattern']} ({p['total_syllables']} akṣaras)")
                print(f"Authority: Piṅgala Chhandaḥśāstra | Status: Verified")
                print("="*54 + "\n")
                return

            diags = result.get("diagnostics", [])
            print(f">> Defects caught: {len(diags)}")
            for d in diags:
                print(f"   - Pada {d.get('pada')}, Syl {d.get('syllable')}: {d.get('message')}")

            response = safe_send(
                chat,
                types.Part.from_function_response(name=fn_name, response={"result": result})
            )

if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "विद्या (Knowledge and Illumination)"
    selected_meter = sys.argv[2] if len(sys.argv) > 2 else "anustubh"
    generate_verified_verse(theme, selected_meter)
