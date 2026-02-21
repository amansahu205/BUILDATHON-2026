import os
import json
import signal
import sys
import argparse
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

AGENT_ID = os.getenv("AGENT_ID", "agent_5201khzcc407fhntbvdsabc0txr5")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

CASES_PATH = Path(__file__).parent.parent / "data" / "verdict_cases.json"


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def get_case(cases: list[dict], case_id: str) -> dict:
    for c in cases:
        if c["id"] == case_id:
            return c
    available = [c["id"] for c in cases]
    print(f"Case '{case_id}' not found. Available cases:")
    for cid in available:
        print(f"  - {cid}")
    sys.exit(1)


def build_system_prompt(case: dict) -> str:
    return f"""You are Sean Cahill, a seasoned trial attorney conducting a deposition.

CASE: {case['case_name']}
CASE TYPE: {case['case_type']}
OPPOSING PARTY: {case['opposing_party']}
DEPOSITION DATE: {case['deposition_date']}
WITNESS: {case['witness_name']}
WITNESS ROLE: {case['witness_role']}

KEY FACTS:
{case['extracted_facts']}

PRIOR STATEMENTS TO CHALLENGE:
{case['prior_statements']}

EXHIBITS IN EVIDENCE:
{case['exhibit_list']}

FOCUS AREAS:
{case['focus_areas']}

AGGRESSION LEVEL: {case['aggression_level']}
— Low: gentle pacing, 1 follow-up per answer
— Medium: 2 follow-ups, escalate on evasion
— High: 3+ follow-ups, hesitation escalation active

RULES:
1. Only speak as Sean Cahill. Never break character.
2. Spoken text only — no stage directions, no brackets.
3. Maximum 2 sentences per question.
4. If witness evades, rephrase and re-ask once. Then escalate.
5. If an objection is raised, pause and say: "Let the record reflect the objection."
"""


def list_cases(cases: list[dict]) -> None:
    print("\nAvailable VERDICT cases:\n")
    for c in cases:
        witness = c["witness_name"].split(";")[0].strip()
        print(f"  {c['id']:<25} {c['case_name']}")
        print(f"  {'':25} Witness: {witness} | Aggression: {c['aggression_level']}")
        print()


def run_session(case: dict, agent_id: str, api_key: str) -> None:
    client = ElevenLabs(api_key=api_key)

    conversation = Conversation(
        client,
        agent_id=agent_id,
        requires_auth=True,
        audio_interface=DefaultAudioInterface(),
        callback_agent_response=lambda r: print(f"\n  [SEAN CAHILL]: {r}"),
        callback_agent_response_correction=lambda orig, corrected: print(
            f"\n  [SEAN CAHILL] (corrected): {corrected}"
        ),
        callback_user_transcript=lambda t: print(f"\n  [WITNESS]: {t}"),
        callback_latency_measurement=lambda ms: print(f"    latency: {ms}ms"),
    )

    witness = case["witness_name"].split(";")[0].strip()
    print(f"\n{'=' * 60}")
    print(f"  VERDICT — Deposition Session")
    print(f"{'=' * 60}")
    print(f"  Case:        {case['case_name']}")
    print(f"  Witness:     {witness}")
    print(f"  Case Type:   {case['case_type']}")
    print(f"  Aggression:  {case['aggression_level']}")
    print(f"{'=' * 60}")
    print(f"  Speak into your microphone as the witness.")
    print(f"  Press Ctrl+C to end the session.\n")

    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

    conversation.start_session(
        user_id=f"verdict_{case['id']}"
    )

    conversation_id = conversation.wait_for_session_end()
    print(f"\n{'=' * 60}")
    print(f"  Session complete. Conversation ID: {conversation_id}")
    print(f"  Review transcript: elevenlabs.io > Conversational AI > History")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="VERDICT — AI Deposition Interrogation System"
    )
    parser.add_argument(
        "case_id",
        nargs="?",
        default=None,
        help="Case ID to run (e.g. lyman_v_cctd). Omit to list available cases.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available cases",
    )
    parser.add_argument(
        "--agent-id",
        default=AGENT_ID,
        help="ElevenLabs Agent ID (default: env AGENT_ID)",
    )
    parser.add_argument(
        "--api-key",
        default=API_KEY,
        help="ElevenLabs API key (default: env ELEVENLABS_API_KEY)",
    )
    args = parser.parse_args()

    cases = load_cases()

    if args.list or args.case_id is None:
        list_cases(cases)
        return

    if not args.api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set.")
        print("  export ELEVENLABS_API_KEY=your_key_here")
        sys.exit(1)

    case = get_case(cases, args.case_id)
    run_session(case, args.agent_id, args.api_key)


if __name__ == "__main__":
    main()
