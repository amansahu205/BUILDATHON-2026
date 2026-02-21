import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { briefsService } from "@/services/briefs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { format, parseISO } from "date-fns";

const BriefsTab = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const { data: briefs, isLoading } = useQuery({
    queryKey: ["briefs", caseId],
    queryFn: () => briefsService.list(caseId!),
    enabled: !!caseId,
  });

  if (isLoading) return <div className="space-y-3">{[1, 2].map((i) => <Skeleton key={i} className="h-24 rounded-lg" />)}</div>;
  if (!briefs?.length) return <p className="text-center text-muted-foreground py-8">No briefs generated yet.</p>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {briefs.map((b) => (
        <Link key={b.id} to={`/briefs/${b.id}`}>
          <Card className="bg-card border-border hover:border-primary/30 transition-colors cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-sans">{b.witnessName}</CardTitle>
                <span className={`text-xl font-bold ${b.sessionScore >= 70 ? "text-verdict-green" : b.sessionScore >= 50 ? "text-primary" : "text-destructive"}`}>
                  {b.sessionScore}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-2">
                <Badge variant="outline">{b.alertTotals.objections} objections</Badge>
                <Badge variant="outline">{b.alertTotals.inconsistencies} inconsistencies</Badge>
              </div>
              <p className="text-xs text-muted-foreground">{format(parseISO(b.createdAt), "MMM d, yyyy 'at' h:mm a")}</p>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
};

export default BriefsTab;
