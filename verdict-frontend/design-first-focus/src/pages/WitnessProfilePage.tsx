import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { witnessesService } from "@/services/witnesses";
import { sessionsService } from "@/services/sessions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, TrendingUp, Settings } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";

const WitnessProfilePage = () => {
  const { caseId, witnessId } = useParams<{ caseId: string; witnessId: string }>();

  const { data: witness, isLoading } = useQuery({
    queryKey: ["witness", caseId, witnessId],
    queryFn: () => witnessesService.get(caseId!, witnessId!),
    enabled: !!caseId && !!witnessId,
  });

  const { data: sessions } = useQuery({
    queryKey: ["sessions", caseId],
    queryFn: () => sessionsService.list(caseId!),
    enabled: !!caseId,
  });

  if (isLoading) return <div className="p-6 space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-40 rounded-lg" />)}</div>;
  if (!witness) return <p className="p-6 text-muted-foreground">Witness not found.</p>;

  const trendData = witness.scoreTrend.map((score, i) => ({ session: i + 1, score }));
  const witnessSessions = sessions?.filter(s => s.witnessId === witnessId) || [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">{witness.name}</h1>
          <p className="text-muted-foreground">{witness.role}</p>
        </div>
        <Button className="bg-gradient-gold text-primary-foreground" asChild>
          <Link to={`/cases/${caseId}/witnesses/${witnessId}/session/new`}>
            <Settings className="mr-2 h-4 w-4" /> Configure Next Session
          </Link>
        </Button>
      </div>

      {witness.plateauAlert && (
        <div className="flex items-center gap-3 rounded-lg bg-verdict-orange/10 border border-verdict-orange/30 p-4">
          <AlertTriangle className="h-5 w-5 text-verdict-orange" />
          <div>
            <p className="font-medium text-sm">Plateau Detected</p>
            <p className="text-xs text-muted-foreground">Score improvement has stalled. Consider adjusting session focus areas or aggression level.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Score Trend */}
        <Card className="bg-card border-border">
          <CardHeader><CardTitle className="text-base font-sans flex items-center gap-2"><TrendingUp className="h-4 w-4" /> Score Trend</CardTitle></CardHeader>
          <CardContent>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trendData}>
                  <XAxis dataKey="session" tick={{ fill: "hsl(215 20% 55%)", fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: "hsl(215 20% 55%)", fontSize: 12 }} />
                  <Line type="monotone" dataKey="score" stroke="hsl(38 92% 50%)" strokeWidth={2} dot={{ fill: "hsl(38 92% 50%)" }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">No sessions yet</p>
            )}
          </CardContent>
        </Card>

        {/* Weakness Map placeholder */}
        <Card className="bg-card border-border">
          <CardHeader><CardTitle className="text-base font-sans">Weakness Map</CardTitle></CardHeader>
          <CardContent className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">
            Radar chart available after first session
          </CardContent>
        </Card>
      </div>

      {/* Session History */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-base font-sans">Session History</CardTitle></CardHeader>
        <CardContent>
          {witnessSessions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No sessions completed.</p>
          ) : (
            <div className="space-y-2">
              {witnessSessions.map((s) => (
                <div key={s.id} className="flex items-center justify-between rounded-md bg-muted/50 px-4 py-3">
                  <div>
                    <p className="text-sm font-medium">{s.config.durationMinutes}min • {s.config.aggressionLevel}</p>
                    <p className="text-xs text-muted-foreground">{s.status}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {s.score != null && <span className="font-bold">{s.score}</span>}
                    {s.briefId && <Link to={`/briefs/${s.briefId}`} className="text-xs text-primary hover:underline">View Brief</Link>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default WitnessProfilePage;
