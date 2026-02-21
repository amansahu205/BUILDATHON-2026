# VERDICT — AI Deposition Interrogation System

Voice-powered legal deposition training system built on [ElevenLabs Conversational AI](https://elevenlabs.io/docs/eleven-agents). An AI attorney (Sean Cahill) conducts depositions against a human witness using real case facts, exhibits, and prior statements.

## Architecture

```
┌──────────────┐     WebRTC / WebSocket     ┌──────────────────────┐
│  React App   │ ◄─────────────────────────► │  ElevenLabs Agent    │
│  (Frontend)  │    voice + transcript       │  verdict_interrogator│
└──────────────┘                             └──────────────────────┘
       │                                              │
       │  case data                                   │  system prompt
       ▼                                              ▼
┌──────────────┐                             ┌──────────────────────┐
│ verdict_     │                             │  Claude Sonnet LLM   │
│ cases.json   │                             │  (via ElevenLabs)    │
└──────────────┘                             └──────────────────────┘

        ── OR ──

┌──────────────┐     Audio (mic/speaker)     ┌──────────────────────┐
│  Python CLI  │ ◄─────────────────────────► │  ElevenLabs Agent    │
│  (agents/)   │    ElevenLabs SDK           │  verdict_interrogator│
└──────────────┘                             └──────────────────────┘
```

## Quick Start

### Prerequisites

- ElevenLabs API key — get one at [elevenlabs.io](https://elevenlabs.io)
- Agent ID: `agent_5201khzcc407fhntbvdsabc0txr5`
- Node.js 18+ (frontend)
- Python 3.10+ (CLI agent)
- PortAudio (for Python mic access): `brew install portaudio` (macOS) or `sudo apt-get install libportaudio2 portaudio19-dev` (Linux)

### Option A — Web Frontend (React + ElevenLabs React SDK)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, pick a case, and click **Start Deposition**. Your browser mic becomes the witness.

### Option B — Python CLI (ElevenLabs Python SDK)

```bash
cd agents
pip install -r requirements.txt

# List available cases
python verdict_session.py --list

# Run a deposition
ELEVENLABS_API_KEY=your_key python verdict_session.py lyman_v_cctd
```

Press `Ctrl+C` to end the session cleanly.

### Option C — Embeddable Widget (zero code)

Drop this into any HTML page:

```html
<script src="https://elevenlabs.io/convai-widget/index.js" async></script>
<elevenlabs-convai agent-id="agent_5201khzcc407fhntbvdsabc0txr5"></elevenlabs-convai>
```

## Available Cases

| ID | Case Name | Type | Aggression |
|----|-----------|------|------------|
| `lyman_v_cctd` | Lyman v. Capital City Transit District | Personal Injury | Medium |
| `utah_v_gunn` | State of Utah v. Derek Gunn | Securities Fraud | High |
| `atlantis_v_tamontes` | Atlantis v. Tamontes Construction | Breach of Contract | Low |
| `reyes_v_haller` | Reyes v. Haller Medical Group | Medical Malpractice | Medium |
| `chen_v_meridian` | Chen v. Meridian Financial Advisors | Elder Financial Abuse | High |

## Project Structure

```
├── agents/
│   ├── verdict_session.py       # Python CLI deposition runner
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile
├── data/
│   └── verdict_cases.json       # Case definitions
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CaseSelector.tsx      # Case picker UI
│   │   │   └── DepositionSession.tsx  # Live deposition with ElevenLabs
│   │   ├── cases.ts             # Case data (mirrors JSON)
│   │   ├── types.ts             # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## Environment Variables

```bash
ELEVENLABS_API_KEY=   # Required for Python CLI; frontend uses public agent
AGENT_ID=             # Defaults to agent_5201khzcc407fhntbvdsabc0txr5
```

## ElevenLabs Agent Configuration

The agent `verdict_interrogator_v1` is configured in the ElevenLabs Console with:

- **Voice**: Custom interrogator voice
- **LLM**: Claude Sonnet
- **System prompt**: Dynamically injected per case via the Python SDK or React SDK overrides
- **First message**: "Good morning. Before we begin, confirm you understand this is a recorded deposition session."

## Docker

```bash
cp .env.example .env
# Fill in your API key
docker compose up
```

Frontend available at http://localhost:5173.
