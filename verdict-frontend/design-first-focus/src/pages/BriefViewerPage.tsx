import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { briefsService } from "@/services/briefs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Download, Share2, MessageSquare, Calendar, Play, Pause, SkipForward, RotateCcw } from "lucide-react";
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from "recharts";
import { useState } from "react";

const BriefViewerPage = () => {
  const { briefId } = useParams<{ briefId: string }>();
  const [playing, setPlaying] = useState(false);

  const { data: brief, isLoading } = useQuery({
    queryKey: ["brief", briefId],
    queryFn: () => briefsService.get(briefId!),
    enabled: !!briefId,
  });

  const downloadPdf = useMutation({
    mutationFn: () => briefsService.downloadPdf(briefId!),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `brief-${briefId}.pdf`;
      a.click();
    },
  });

  const share = useMutation({
    mutationFn: () => briefsService.shareWithWitness(briefId!),
  });

  if (isLoading) return <div className="p-6 space-y-4">{[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-40 rounded-lg" />)}</div>;
  if (!brief) return <p className="p-6 text-muted-foreground">Brief not found.</p>;

  const scoreColor = brief.sessionScore >= 70 ? "text-verdict-green" : brief.sessionScore >= 50 ? "text-primary" : "text-destructive";

  const radarData = [
    { axis: "Timeline", value: brief.weaknessMap.timeline },
    { axis: "Financial", value: brief.weaknessMap.financial },
    { axis: "Communications", value: brief.weaknessMap.communications },
    { axis: "Relationships", value: brief.weaknessMap.relationships },
    { axis: "Actions", value: brief.weaknessMap.actions },
    { axis: "Prior Stmts", value: brief.weaknessMap.priorStatements },
    ...(brief.weaknessMap.composure != null ? [{ axis: "Composure", value: brief.weaknessMap.composure }] : []),
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Actions Bar */}
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-bold">Coaching Brief</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => downloadPdf.mutate()}><Download className="mr-1 h-3 w-3" /> PDF</Button>
          <Button variant="outline" size="sm" onClick={() => share.mutate()}><Share2 className="mr-1 h-3 w-3" /> Share</Button>
          <Button variant="outline" size="sm"><MessageSquare className="mr-1 h-3 w-3" /> Annotate</Button>
          <Button variant="outline" size="sm"><Calendar className="mr-1 h-3 w-3" /> Schedule Next</Button>
        </div>
      </div>

      {/* Score Summary */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="grid grid-cols-4 gap-6 text-center">
            <div>
              <p className={`text-4xl font-bold ${scoreColor}`}>{brief.sessionScore}</p>
              <p className="text-xs text-muted-foreground mt-1">Session Score</p>
            </div>
            <div>
              <p className={`text-2xl font-bold ${brief.deltaFromFirst >= 0 ? "text-verdict-green" : "text-destructive"}`}>
                {brief.deltaFromFirst >= 0 ? "+" : ""}{brief.deltaFromFirst}
              </p>
              <p className="text-xs text-muted-foreground mt-1">vs Session 1</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{brief.consistencyRate}%</p>
              <p className="text-xs text-muted-foreground mt-1">Consistency</p>
            </div>
            <div>
              <div className="flex justify-center gap-2">
                <Badge variant="outline">{brief.alertTotals.objections} obj</Badge>
                <Badge variant="outline">{brief.alertTotals.inconsistencies} inc</Badge>
                <Badge variant="outline">{brief.alertTotals.behavioral} beh</Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Alerts</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inconsistencies */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Inconsistencies</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {brief.inconsistencies.filter(i => i.confirmed).map((inc) => (
            <div key={inc.id} className="rounded-md border border-border p-4 space-y-2">
              <div className="flex items-center justify-between">
                <Badge variant={inc.impeachmentRisk === "high" ? "destructive" : inc.impeachmentRisk === "medium" ? "default" : "secondary"}>
                  {inc.impeachmentRisk} risk
                </Badge>
                <span className="text-xs text-muted-foreground">Confidence: {(inc.confidenceScore * 100).toFixed(0)}%</span>
              </div>
              <p className="text-sm"><span className="bg-destructive/20 px-1 rounded">{inc.highlightedPhrase}</span></p>
              <blockquote className="text-xs italic text-muted-foreground border-l-2 border-primary pl-3">
                "{inc.priorStatementQuote}" — {inc.priorSource} {inc.priorPageLine}
              </blockquote>
              <p className="text-xs text-muted-foreground">{inc.coachNote}</p>
            </div>
          ))}
          {brief.inconsistencies.filter(i => i.confirmed).length === 0 && (
            <p className="text-sm text-muted-foreground">No confirmed inconsistencies.</p>
          )}
        </CardContent>
      </Card>

      {/* Objections */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Objections</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {brief.objections.map((obj) => (
            <div key={obj.id} className="rounded-md border border-border p-4 space-y-2">
              <div className="flex items-center gap-2">
                <Badge>{obj.freRule}</Badge>
                <span className="text-xs text-muted-foreground">Rate: {(obj.objectionRate * 100).toFixed(0)}%</span>
              </div>
              <p className="text-sm">{obj.questionText}</p>
              <p className="text-xs text-muted-foreground">{obj.trainingNote}</p>
            </div>
          ))}
          {brief.objections.length === 0 && <p className="text-sm text-muted-foreground">No objection events.</p>}
        </CardContent>
      </Card>

      {/* Weakness Map */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Weakness Map</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="hsl(217 30% 18%)" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "hsl(215 20% 55%)", fontSize: 11 }} />
              <Radar dataKey="value" stroke="hsl(38 92% 50%)" fill="hsl(38 92% 50%)" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Top Coaching Recommendations</CardTitle></CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-3">
            {brief.recommendations.map((rec, i) => (
              <li key={i} className="text-sm">{rec}</li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {/* Coach Narration Player */}
      {brief.coachNarrationUrl && (
        <Card className="bg-card border-border">
          <CardContent className="flex items-center gap-4 pt-6">
            <Button size="icon" variant="outline" onClick={() => setPlaying(!playing)}>
              {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
            <div className="flex-1 h-2 rounded-full bg-muted">
              <div className="h-full w-0 rounded-full bg-primary transition-all" />
            </div>
            <Button size="icon" variant="ghost"><SkipForward className="h-4 w-4" /></Button>
            <Button size="icon" variant="ghost"><RotateCcw className="h-4 w-4" /></Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BriefViewerPage;
