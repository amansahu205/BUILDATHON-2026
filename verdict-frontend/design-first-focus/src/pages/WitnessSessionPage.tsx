import { useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Mic, MicOff, Pause, User } from "lucide-react";

type WitnessState = "waiting" | "active" | "paused" | "complete";

const WitnessSessionPage = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const { data: session, isLoading } = useQuery({
    queryKey: ["witness-session", sessionId],
    queryFn: () => sessionsService.getWitnessSession(sessionId!, token),
    enabled: !!sessionId && !!token,
  });

  // Placeholder local state
  const [state, setState] = useState<WitnessState>("waiting");
  const [isSpeaking, setIsSpeaking] = useState(false);

  if (isLoading) return <div className="flex min-h-screen items-center justify-center"><Skeleton className="h-64 w-64 rounded-full" /></div>;

  if (!session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground">Invalid or expired session link.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4">
      {/* Avatar */}
      <div className="relative mb-8">
        <div className={cn(
          "h-32 w-32 rounded-full bg-muted flex items-center justify-center",
          state === "active" && "ring-4 ring-primary/30"
        )}>
          <User className="h-16 w-16 text-muted-foreground" />
        </div>
        {state === "active" && (
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2">
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="w-1 bg-primary rounded-full animate-pulse" style={{ height: `${8 + Math.random() * 16}px`, animationDelay: `${i * 0.1}s` }} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Status */}
      <h2 className="text-xl font-semibold mb-2">
        {state === "waiting" && "Waiting to begin…"}
        {state === "active" && (isSpeaking ? "Your Turn" : "Listening…")}
        {state === "paused" && "Session Paused"}
        {state === "complete" && "Session Complete"}
      </h2>

      {/* Mic indicator */}
      {state === "active" && (
        <div className={cn("flex items-center gap-2 mb-6 px-4 py-2 rounded-full", isSpeaking ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground")}>
          {isSpeaking ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
          <span className="text-sm">{isSpeaking ? "Speaking" : "Mic off"}</span>
        </div>
      )}

      {/* Timer */}
      <p className="text-3xl font-mono font-bold text-muted-foreground mb-8">
        {session.config.durationMinutes}:00
      </p>

      {/* Pause */}
      {state === "active" && (
        <Button variant="outline" onClick={() => setState("paused")}>
          <Pause className="mr-2 h-4 w-4" /> Need a Moment
        </Button>
      )}

      {state === "complete" && (
        <p className="text-muted-foreground text-sm">Thank you for your participation. You may close this window.</p>
      )}
    </div>
  );
};

export default WitnessSessionPage;
