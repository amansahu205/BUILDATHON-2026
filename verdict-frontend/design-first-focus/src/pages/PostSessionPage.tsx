import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { briefsService } from "@/services/briefs";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, Loader2 } from "lucide-react";

const STEPS = ["Analyzing transcript", "Cross-referencing documents", "Generating coaching insights", "Building brief"];

const PostSessionPage = () => {
  const { caseId, sessionId } = useParams<{ caseId: string; sessionId: string }>();
  const navigate = useNavigate();

  const { data: status } = useQuery({
    queryKey: ["brief-status", sessionId],
    queryFn: () => briefsService.getGenerationStatus(sessionId!),
    enabled: !!sessionId,
    refetchInterval: 3000,
  });

  const progress = status?.progress ?? 0;
  const currentStep = Math.min(Math.floor(progress / 25), 3);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-6 text-center">
        <CheckCircle2 className="h-12 w-12 text-verdict-green mx-auto" />
        <h1 className="font-display text-2xl font-bold">Session Complete</h1>

        <Card className="bg-card border-border">
          <CardContent className="pt-6 space-y-4">
            {STEPS.map((step, i) => (
              <div key={step} className="flex items-center gap-3">
                {i < currentStep ? (
                  <CheckCircle2 className="h-5 w-5 text-verdict-green shrink-0" />
                ) : i === currentStep ? (
                  <Loader2 className="h-5 w-5 text-primary animate-spin shrink-0" />
                ) : (
                  <div className="h-5 w-5 rounded-full border border-border shrink-0" />
                )}
                <span className={`text-sm ${i <= currentStep ? "text-foreground" : "text-muted-foreground"}`}>{step}</span>
              </div>
            ))}

            {status?.eta && (
              <p className="text-xs text-muted-foreground mt-4">Estimated time: {status.eta}s</p>
            )}
          </CardContent>
        </Card>

        <Button
          className="w-full bg-gradient-gold text-primary-foreground shadow-gold"
          disabled={!status?.briefId}
          onClick={() => status?.briefId && navigate(`/briefs/${status.briefId}`)}
        >
          {status?.briefId ? "View Brief" : "Generating…"}
        </Button>
      </div>
    </div>
  );
};

export default PostSessionPage;
