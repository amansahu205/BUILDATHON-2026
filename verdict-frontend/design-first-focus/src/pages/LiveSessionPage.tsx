import { useParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Pause, Play, SkipForward, Square, Send, Wifi, WifiOff, AlertTriangle, Mic, MicOff } from "lucide-react";
import type { LiveSessionState } from "@/types";

const EMPTY_LIVE_STATE: LiveSessionState = {
  status: "active",
  elapsedSeconds: 0,
  totalSeconds: 1800,
  currentTopic: "PRIOR_STATEMENTS",
  questionCount: 0,
  transcript: [],
  alerts: [],
  witnessConnected: true,
  serviceStatus: { elevenlabs: true, nemotron: true, nia: true },
};

const LiveSessionPage = () => {
  const { caseId, sessionId } = useParams<{ caseId: string; sessionId: string }>();
  const [note, setNote] = useState("");
  const transcriptRef = useRef<HTMLDivElement>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const recordStartedAtRef = useRef<number>(0);
  const [isRecording, setIsRecording] = useState(false);
  const [state, setState] = useState<LiveSessionState>(EMPTY_LIVE_STATE);
  const [questionText, setQuestionText] = useState("");

  const { data: liveState } = useQuery({
    queryKey: ["live-state", sessionId],
    queryFn: () => sessionsService.getLiveState(sessionId!),
    enabled: !!sessionId,
    refetchInterval: 2000,
  });

  useEffect(() => {
    if (liveState) setState(liveState);
  }, [liveState]);

  const pause = useMutation({ mutationFn: () => sessionsService.pause(caseId!, sessionId!) });
  const resume = useMutation({ mutationFn: () => sessionsService.resume(caseId!, sessionId!) });
  const end = useMutation({ mutationFn: () => sessionsService.end(caseId!, sessionId!) });
  const skipTopic = useMutation({ mutationFn: () => sessionsService.skipTopic(caseId!, sessionId!) });
  const addNote = useMutation({ mutationFn: (n: string) => sessionsService.addNote(caseId!, sessionId!, n) });
  const uploadAudio = useMutation({
    mutationFn: ({ blob, durationMs }: { blob: Blob; durationMs: number }) =>
      sessionsService.uploadAnswerAudio(sessionId!, blob, state.questionCount || 0, durationMs),
  });
  const nextQuestion = useMutation({
    mutationFn: async () =>
      sessionsService.streamQuestion(
        sessionId!,
        {
          questionNumber: (state.questionCount || 0) + 1,
          priorAnswer:
            [...state.transcript]
              .reverse()
              .find((t) => t.speaker === "witness")?.text || undefined,
          currentTopic: state.currentTopic || "PRIOR_STATEMENTS",
        },
        (event) => {
          if (event.type === "QUESTION_END" && typeof event.fullText === "string") {
            setQuestionText(event.fullText);
          }
          if (event.type === "QUESTION_AUDIO" && typeof event.audioBase64 === "string") {
            const a = new Audio(`data:audio/mpeg;base64,${event.audioBase64}`);
            a.play().catch(() => {});
          }
        },
      ),
  });

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

  const toggleRecording = async () => {
    if (!isRecording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];
      rec.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };
      rec.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const durationMs = Math.max(1, Date.now() - recordStartedAtRef.current);
        if (blob.size > 0) {
          await uploadAudio.mutateAsync({ blob, durationMs });
        }
        stream.getTracks().forEach((t) => t.stop());
      };
      recorderRef.current = rec;
      recordStartedAtRef.current = Date.now();
      rec.start();
      setIsRecording(true);
    } else if (recorderRef.current) {
      recorderRef.current.stop();
      setIsRecording(false);
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
            <Button
              variant={isRecording ? "destructive" : "outline"}
              className="w-full"
              size="sm"
              onClick={() => toggleRecording()}
            >
              {isRecording ? <MicOff className="mr-2 h-3 w-3" /> : <Mic className="mr-2 h-3 w-3" />}
              {isRecording ? "Stop & Upload" : "Record Answer"}
            </Button>
            <Button
              variant="outline"
              className="w-full"
              size="sm"
              onClick={() => nextQuestion.mutate()}
            >
              <Play className="mr-2 h-3 w-3" /> Next Question
            </Button>
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
            {questionText && (
              <div className="mb-3 rounded-md border border-primary/30 bg-primary/5 p-3 text-sm">
                <span className="text-xs font-medium text-primary uppercase mr-2">interrogator</span>
                <p className="mt-1">{questionText}</p>
              </div>
            )}
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
