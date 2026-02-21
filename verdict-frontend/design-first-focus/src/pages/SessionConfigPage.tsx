import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { sessionsService } from "@/services/sessions";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { FocusArea, AggressionLevel, SessionConfig } from "@/types";
import { FOCUS_AREA_LABELS } from "@/types";

const DURATIONS = [15, 30, 45, 60] as const;
const AGGRESSION_LEVELS: { value: AggressionLevel; label: string; desc: string }[] = [
  { value: "standard", label: "Standard", desc: "Typical deposition questioning" },
  { value: "elevated", label: "Elevated", desc: "More aggressive cross-examination" },
  { value: "high_stakes", label: "High-Stakes", desc: "Maximum pressure simulation" },
];

const SessionConfigPage = () => {
  const { caseId, witnessId } = useParams<{ caseId: string; witnessId: string }>();
  const navigate = useNavigate();

  const [duration, setDuration] = useState<15 | 30 | 45 | 60>(30);
  const [focusAreas, setFocusAreas] = useState<FocusArea[]>([]);
  const [aggression, setAggression] = useState<AggressionLevel>("standard");
  const [objectionCopilot, setObjectionCopilot] = useState(true);
  const [behavioralSentinel, setBehavioralSentinel] = useState(false);

  const toggleFocus = (area: FocusArea) => {
    setFocusAreas(prev => prev.includes(area) ? prev.filter(a => a !== area) : [...prev, area]);
  };

  const create = useMutation({
    mutationFn: () => {
      const config: SessionConfig = {
        witnessId: witnessId!,
        durationMinutes: duration,
        focusAreas,
        aggressionLevel: aggression,
        objectionCopilot,
        behavioralSentinel,
      };
      return sessionsService.create(caseId!, config);
    },
    onSuccess: (session) => {
      navigate(`/cases/${caseId}/session/${session.id}/lobby`);
    },
  });

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="font-display text-2xl font-bold">Configure Session</h1>

      {/* Duration */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-base font-sans">Duration</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {DURATIONS.map(d => (
              <Button key={d} variant={duration === d ? "default" : "outline"} className={cn(duration === d && "bg-gradient-gold text-primary-foreground")} onClick={() => setDuration(d)}>
                {d} min
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Focus Areas */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-base font-sans">Focus Areas</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {(Object.entries(FOCUS_AREA_LABELS) as [FocusArea, string][]).map(([key, label]) => (
              <Badge
                key={key}
                variant={focusAreas.includes(key) ? "default" : "outline"}
                className={cn("cursor-pointer select-none", focusAreas.includes(key) && "bg-primary text-primary-foreground")}
                onClick={() => toggleFocus(key)}
              >
                {label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Aggression */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-base font-sans">Interrogator Aggression</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {AGGRESSION_LEVELS.map(level => (
            <button
              key={level.value}
              onClick={() => setAggression(level.value)}
              className={cn(
                "w-full text-left rounded-md border px-4 py-3 transition-colors",
                aggression === level.value ? "border-primary bg-primary/10" : "border-border hover:border-primary/30"
              )}
            >
              <p className="font-medium text-sm">{level.label}</p>
              <p className="text-xs text-muted-foreground">{level.desc}</p>
            </button>
          ))}
        </CardContent>
      </Card>

      {/* Toggles */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-center justify-between"><Label>Objection Copilot</Label><Switch checked={objectionCopilot} onCheckedChange={setObjectionCopilot} /></div>
          <div className="flex items-center justify-between">
            <div><Label>Behavioral Sentinel</Label><p className="text-xs text-muted-foreground">Requires firm-level activation</p></div>
            <Switch checked={behavioralSentinel} onCheckedChange={setBehavioralSentinel} />
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" disabled={create.isPending}>Generate Practice Link</Button>
        <Button className="flex-1 bg-gradient-gold text-primary-foreground" onClick={() => create.mutate()} disabled={create.isPending}>
          {create.isPending ? "Creating…" : "Start Session as Attorney"}
        </Button>
      </div>
    </div>
  );
};

export default SessionConfigPage;
