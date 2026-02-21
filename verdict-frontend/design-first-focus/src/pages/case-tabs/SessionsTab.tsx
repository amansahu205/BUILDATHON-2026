import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { format, parseISO } from "date-fns";

const SessionsTab = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const { data: sessions, isLoading } = useQuery({
    queryKey: ["sessions", caseId],
    queryFn: () => sessionsService.list(caseId!),
    enabled: !!caseId,
  });

  if (isLoading) return <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 rounded-lg" />)}</div>;
  if (!sessions?.length) return <p className="text-center text-muted-foreground py-8">No sessions yet.</p>;

  return (
    <div className="space-y-3">
      {sessions.map((s) => (
        <Card key={s.id} className="bg-card border-border">
          <CardContent className="flex items-center gap-4 py-4">
            <div className="flex-1">
              <p className="font-medium">{s.witnessName}</p>
              <p className="text-xs text-muted-foreground">
                {s.config.durationMinutes}min • {s.config.aggressionLevel} • {s.createdAt ? format(parseISO(s.createdAt), "MMM d, yyyy") : ""}
              </p>
            </div>
            <Badge variant={s.status === "complete" ? "default" : "secondary"}>{s.status}</Badge>
            {s.score != null && (
              <span className={`text-lg font-bold ${s.score >= 70 ? "text-verdict-green" : s.score >= 50 ? "text-primary" : "text-destructive"}`}>
                {s.score}
              </span>
            )}
            {s.briefId && (
              <Link to={`/briefs/${s.briefId}`} className="text-xs text-primary hover:underline">View Brief</Link>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default SessionsTab;
