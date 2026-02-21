import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Copy, Mail, Play, UserX } from "lucide-react";
import { FOCUS_AREA_LABELS } from "@/types";
import { useNavigate } from "react-router-dom";
import { toast } from "@/hooks/use-toast";

const SessionLobbyPage = () => {
  const { caseId, sessionId } = useParams<{ caseId: string; sessionId: string }>();
  const navigate = useNavigate();

  const { data: lobby, isLoading } = useQuery({
    queryKey: ["lobby", caseId, sessionId],
    queryFn: () => sessionsService.getLobby(caseId!, sessionId!),
    enabled: !!caseId && !!sessionId,
    refetchInterval: 5000,
  });

  const startSession = (withoutWitness?: boolean) => {
    sessionsService.start(caseId!, sessionId!, withoutWitness).then(() => {
      navigate(`/cases/${caseId}/session/${sessionId}/live`);
    });
  };

  const copyLink = () => {
    if (lobby?.practiceLink) {
      navigator.clipboard.writeText(lobby.practiceLink);
      toast({ title: "Link copied", description: "Practice link copied to clipboard." });
    }
  };

  if (isLoading) return <div className="p-6"><Skeleton className="h-64 rounded-lg" /></div>;
  if (!lobby) return <p className="p-6 text-muted-foreground">Session not found.</p>;

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="font-display text-2xl font-bold">Session Lobby</h1>

      <Card className="bg-card border-border">
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><p className="text-muted-foreground">Case</p><p className="font-medium">{lobby.caseName}</p></div>
            <div><p className="text-muted-foreground">Witness</p><p className="font-medium">{lobby.session.witnessName}</p></div>
            <div><p className="text-muted-foreground">Duration</p><p className="font-medium">{lobby.session.config.durationMinutes} min</p></div>
            <div><p className="text-muted-foreground">Aggression</p><p className="font-medium capitalize">{lobby.session.config.aggressionLevel}</p></div>
            <div><p className="text-muted-foreground">Docs Indexed</p><p className="font-medium">{lobby.documentsIndexed}</p></div>
            <div><p className="text-muted-foreground">Prior Sessions</p><p className="font-medium">{lobby.priorSessionCount}</p></div>
          </div>

          <div>
            <p className="text-muted-foreground text-sm mb-2">Focus Areas</p>
            <div className="flex flex-wrap gap-2">
              {lobby.session.config.focusAreas.map(a => (
                <Badge key={a} variant="secondary">{FOCUS_AREA_LABELS[a]}</Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="text-muted-foreground text-sm mb-2">Features</p>
            <div className="flex gap-2">
              {lobby.session.config.objectionCopilot && <Badge>Objection Copilot</Badge>}
              {lobby.session.config.behavioralSentinel && <Badge variant="outline">Behavioral Sentinel</Badge>}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Witness status */}
      <Card className="bg-card border-border">
        <CardContent className="flex items-center justify-between pt-6">
          <div className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${lobby.witnessConnected ? "bg-verdict-green" : "bg-muted-foreground animate-pulse"}`} />
            <span className="text-sm">{lobby.witnessConnected ? "Witness connected" : "Waiting for witness…"}</span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={copyLink}><Copy className="mr-1 h-3 w-3" /> Copy Link</Button>
            <Button variant="outline" size="sm"><Mail className="mr-1 h-3 w-3" /> Resend Email</Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button
          className="flex-1 bg-gradient-gold text-primary-foreground shadow-gold"
          disabled={!lobby.witnessConnected}
          onClick={() => startSession()}
        >
          <Play className="mr-2 h-4 w-4" /> Begin Session
        </Button>
        <Button variant="outline" onClick={() => startSession(true)}>
          <UserX className="mr-2 h-4 w-4" /> Without Witness
        </Button>
      </div>
    </div>
  );
};

export default SessionLobbyPage;
