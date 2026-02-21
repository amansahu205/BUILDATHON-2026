import { useConversation } from "@elevenlabs/react";
import { useCallback, useEffect, useRef, useState } from "react";
import type { VerdictCase, TranscriptEntry } from "../types";

const AGENT_ID = "agent_5201khzcc407fhntbvdsabc0txr5";

interface DepositionSessionProps {
  activeCase: VerdictCase;
  onEnd: () => void;
}

export default function DepositionSession({ activeCase, onEnd }: DepositionSessionProps) {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [sessionDuration, setSessionDuration] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval>>(undefined);

  const addEntry = useCallback((speaker: "agent" | "witness", text: string) => {
    setTranscript((prev) => [...prev, { speaker, text, timestamp: new Date() }]);
  }, []);

  const conversation = useConversation({
    onConnect: () => {
      setSessionActive(true);
      timerRef.current = setInterval(() => setSessionDuration((s) => s + 1), 1000);
    },
    onDisconnect: () => {
      setSessionActive(false);
      if (timerRef.current) clearInterval(timerRef.current);
    },
    onMessage: (message) => {
      if (message.source === "ai") {
        addEntry("agent", message.message);
      } else {
        addEntry("witness", message.message);
      }
    },
    onError: (error) => {
      console.error("ElevenLabs error:", error);
    },
  });

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [transcript]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startSession = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      await conversation.startSession({
        agentId: AGENT_ID,
        connectionType: "webrtc",
      });
    } catch (err) {
      console.error("Failed to start session:", err);
      alert("Microphone access is required. Please allow microphone access and try again.");
    }
  };

  const endSession = async () => {
    await conversation.endSession();
    setSessionActive(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const witness = activeCase.witness_name.split(";")[0].trim();

  const aggressionBarWidth =
    activeCase.aggression_level === "Low"
      ? "33%"
      : activeCase.aggression_level === "Medium"
        ? "66%"
        : "100%";

  const aggressionColor =
    activeCase.aggression_level === "Low"
      ? "#22c55e"
      : activeCase.aggression_level === "Medium"
        ? "#f59e0b"
        : "#ef4444";

  return (
    <div className="deposition-session">
      <header className="session-header">
        <button className="back-btn" onClick={() => { endSession(); onEnd(); }}>
          Exit
        </button>
        <div className="session-title">
          <h2>{activeCase.case_name}</h2>
          <span className="session-type">{activeCase.case_type}</span>
        </div>
        <div className="session-controls">
          {sessionActive && (
            <div className="recording-indicator">
              <span className="rec-dot" />
              REC {formatTime(sessionDuration)}
            </div>
          )}
        </div>
      </header>

      <div className="session-body">
        <aside className="case-sidebar">
          <section className="sidebar-section">
            <h4>Witness</h4>
            <p className="witness-name">{witness}</p>
            <p className="witness-role">{activeCase.witness_role}</p>
          </section>

          <section className="sidebar-section">
            <h4>Aggression Level</h4>
            <div className="aggression-meter">
              <div
                className="aggression-fill"
                style={{ width: aggressionBarWidth, backgroundColor: aggressionColor }}
              />
            </div>
            <span className="aggression-label" style={{ color: aggressionColor }}>
              {activeCase.aggression_level}
            </span>
          </section>

          <section className="sidebar-section">
            <h4>Focus Areas</h4>
            <ul className="focus-list">
              {activeCase.focus_areas.split(";").map((area, i) => (
                <li key={i}>{area.trim()}</li>
              ))}
            </ul>
          </section>

          <section className="sidebar-section">
            <h4>Exhibits</h4>
            <ul className="exhibit-list">
              {activeCase.exhibit_list.split(";").map((ex, i) => (
                <li key={i}>{ex.trim()}</li>
              ))}
            </ul>
          </section>
        </aside>

        <main className="conversation-area">
          <div className="transcript" ref={transcriptRef}>
            {transcript.length === 0 && sessionActive && (
              <div className="transcript-placeholder">
                <p>Deposition in progress. Speak as the witness.</p>
              </div>
            )}
            {transcript.length === 0 && !sessionActive && (
              <div className="transcript-placeholder">
                <p>Press Start Deposition to begin the session.</p>
              </div>
            )}
            {transcript.map((entry, i) => (
              <div key={i} className={`transcript-entry ${entry.speaker}`}>
                <div className="entry-header">
                  <span className="speaker-label">
                    {entry.speaker === "agent" ? "SEAN CAHILL" : "WITNESS"}
                  </span>
                  <span className="entry-time">
                    {entry.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                  </span>
                </div>
                <p className="entry-text">{entry.text}</p>
              </div>
            ))}
          </div>

          <div className="session-footer">
            <div className="status-bar">
              <div className={`status-dot ${conversation.status === "connected" ? "connected" : ""}`} />
              <span className="status-text">
                {conversation.status === "connected"
                  ? conversation.isSpeaking
                    ? "Sean Cahill is speaking..."
                    : "Listening for witness testimony..."
                  : "Disconnected"}
              </span>
            </div>

            <div className="action-buttons">
              {!sessionActive ? (
                <button className="btn-primary" onClick={startSession}>
                  Start Deposition
                </button>
              ) : (
                <button className="btn-danger" onClick={endSession}>
                  End Session
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
