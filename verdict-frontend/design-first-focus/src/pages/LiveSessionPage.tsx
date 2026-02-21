import { useParams } from "react-router-dom";
import { useState, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { MOCK_LIVE_SESSION } from "@/mocks/data";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Pause, Play, SkipForward, Square, Send, Wifi, WifiOff, AlertTriangle } from "lucide-react";
import type { LiveSessionState, LiveAlert } from "@/types";

const LiveSessionPage = () => {
  const { caseId, sessionId } = useParams<{ caseId: string; sessionId: string }>();
  const [note, setNote] = useState("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  // Use mock live session data for demo
  const [state, setState] = useState<LiveSessionState>(MOCK_LIVE_SESSION);

  const pause = useMutation({ mutationFn: () => sessionsService.pause(caseId!, sessionId!) });
  const resume = useMutation({ mutationFn: () => sessionsService.resume(caseId!, sessionId!) });
  const end = useMutation({ mutationFn: () => sessionsService.end(caseId!, sessionId!) });
  const skipTopic = useMutation({ mutationFn: () => sessionsService.skipTopic(caseId!, sessionId!) });
  const addNote = useMutation({ mutationFn: (n: string) => sessionsService.addNote(caseId!, sessionId!, n) });

  const formatTime = (s: number) => `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
  const remaining = state.totalSeconds - state.elapsedSeconds;
  const timerColor = remaining < 300 ? "text-destructive" : remaining < 600 ? "text-primary" : "text-foreground";

  const getAlertIcon = (type: string) => {
    if (type === "objection") return "🔴";
    if (type === "inconsistency") return "🟡";
    return "🟠";
  };

  const handleAddNote = () => {
    if (note.trim()) {
      addNote.mutate(note.trim());
      setNote("");
    }
  };

  // Service degradation banners
  const degraded = !state.serviceStatus.elevenlabs || !state.serviceStatus.nemotron || !state.serviceStatus.nia;

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Degradation banner */}
      {degraded && (
        <div className="flex items-center gap-2 bg-verdict-orange/10 border-b border-verdict-orange/30 px-4 py-2 text-sm">
          <AlertTriangle className="h-4 w-4 text-verdict-orange" />
          <span>
            {!state.serviceStatus.elevenlabs && "ElevenLabs unavailable. "}
            {!state.serviceStatus.nemotron && "Nemotron unavailable. "}
            {!state.serviceStatus.nia && "Nia offline. "}
            Some features may be degraded.
          </span>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel — Controls (220px) */}
        <div className="w-[220px] shrink-0 border-r border-border bg-card p-4 flex flex-col gap-4">
          {/* Connection */}
          <div className="flex items-center gap-2 text-xs">
            {state.witnessConnected ? <Wifi className="h-3 w-3 text-verdict-green" /> : <WifiOff className="h-3 w-3 text-destructive" />}
            <span className="text-muted-foreground">{state.status}</span>
          </div>

          {/* Timer */}
          <div className="text-center">
            <p className={cn("text-3xl font-mono font-bold", timerColor)}>{formatTime(remaining)}</p>
            <p className="text-xs text-muted-foreground mt-1">remaining</p>
          </div>

          {/* Topic */}
          <div>
            <p className="text-xs text-muted-foreground">Current Topic</p>
            <p className="text-sm font-medium mt-1">{state.currentTopic}</p>
          </div>

          {/* Question count */}
          <div>
            <p className="text-xs text-muted-foreground">Questions</p>
            <p className="text-lg font-bold">{state.questionCount}</p>
          </div>

          {/* Controls */}
          <div className="space-y-2 mt-auto">
            {state.status === "active" ? (
              <Button variant="outline" className="w-full" size="sm" onClick={() => pause.mutate()}>
                <Pause className="mr-2 h-3 w-3" /> Pause
              </Button>
            ) : state.status === "paused" ? (
              <Button variant="outline" className="w-full" size="sm" onClick={() => resume.mutate()}>
                <Play className="mr-2 h-3 w-3" /> Resume
              </Button>
            ) : null}
            <Button variant="outline" className="w-full" size="sm" onClick={() => skipTopic.mutate()}>
              <SkipForward className="mr-2 h-3 w-3" /> Skip Topic
            </Button>
            <Button variant="destructive" className="w-full" size="sm" onClick={() => end.mutate()}>
              <Square className="mr-2 h-3 w-3" /> End Early
            </Button>
          </div>
        </div>

        {/* Center Panel — Transcript */}
        <div className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 p-4" ref={transcriptRef}>
            {state.transcript.length === 0 ? (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <p>Waiting for session to begin…</p>
              </div>
            ) : (
              <div className="space-y-3">
                {state.transcript.map((entry) => (
                  <div
                    key={entry.id}
                    className={cn(
                      "rounded-md p-3 text-sm",
                      entry.flagged && "border-l-2 border-destructive bg-destructive/5",
                      entry.speaker === "interrogator" && "bg-muted/50",
                      entry.speaker === "witness" && "bg-card",
                      entry.speaker === "system" && "text-muted-foreground italic text-xs"
                    )}
                  >
                    <span className="text-xs font-medium text-muted-foreground uppercase mr-2">
                      {entry.speaker}
                    </span>
                    <span className="text-xs text-muted-foreground mr-2">{formatTime(entry.timestamp)}</span>
                    <p className="mt-1">{entry.text}</p>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>

          {/* Bottom bar — Note */}
          <div className="border-t border-border p-3 flex gap-2">
            <Input
              placeholder="Add timestamped note…"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddNote()}
              className="flex-1"
            />
            <Button size="icon" variant="outline" onClick={handleAddNote}><Send className="h-4 w-4" /></Button>
          </div>
        </div>

        {/* Right Panel — Alert Rail (320px) */}
        <div className="w-[320px] shrink-0 border-l border-border bg-card flex flex-col">
          <div className="p-3 border-b border-border">
            <h3 className="font-semibold text-sm">Live Alerts</h3>
          </div>
          <ScrollArea className="flex-1">
            {state.alerts.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground text-sm">No alerts yet</div>
            ) : (
              <div className="p-2 space-y-2">
                {state.alerts.map((alert) => (
                  <div key={alert.id} className="rounded-md border border-border p-3 text-sm animate-slide-in-right">
                    <div className="flex items-start gap-2">
                      <span>{getAlertIcon(alert.type)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-xs">{alert.title}</p>
                          {alert.experimentalLabel && <Badge variant="outline" className="text-[10px] px-1">experimental</Badge>}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{alert.description}</p>
                        {alert.freRule && <Badge className="mt-1 text-[10px]">{alert.freRule}</Badge>}
                        {alert.confidenceScore != null && (
                          <p className="text-[10px] text-muted-foreground mt-1">Confidence: {(alert.confidenceScore * 100).toFixed(0)}%</p>
                        )}
                        {alert.priorQuote && (
                          <blockquote className="text-[10px] italic text-muted-foreground mt-1 border-l-2 border-primary pl-2">
                            "{alert.priorQuote}" — {alert.priorSource} {alert.priorPageLine}
                          </blockquote>
                        )}
                        {alert.auCodes && (
                          <p className="text-[10px] text-muted-foreground mt-1">AU Codes: {alert.auCodes.join(", ")}</p>
                        )}
                        <div className="flex gap-1 mt-2">
                          <Button size="sm" variant="outline" className="h-6 text-[10px] px-2">Confirm</Button>
                          <Button size="sm" variant="outline" className="h-6 text-[10px] px-2">Reject</Button>
                          <Button size="sm" variant="ghost" className="h-6 text-[10px] px-2">Dismiss</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </div>
    </div>
  );
};

export default LiveSessionPage;
