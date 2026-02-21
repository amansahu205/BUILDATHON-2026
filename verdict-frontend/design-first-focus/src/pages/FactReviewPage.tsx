import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { casesService } from "@/services/cases";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CheckCircle2, AlertTriangle } from "lucide-react";

const FactReviewPage = () => {
  const { caseId } = useParams<{ caseId: string }>();

  const { data: facts, isLoading } = useQuery({
    queryKey: ["facts", caseId],
    queryFn: () => casesService.getFactReview(caseId!),
    enabled: !!caseId,
  });

  if (isLoading) return <div className="p-6 space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-32 rounded-lg" />)}</div>;
  if (!facts) return <p className="p-6 text-muted-foreground">Unable to load fact review.</p>;

  return (
    <div className="p-6 space-y-8">
      <h1 className="font-display text-2xl font-bold">Fact Review</h1>

      {/* Parties */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Parties</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {facts.parties.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell>{p.role}</TableCell>
                  <TableCell>{p.confirmed ? <CheckCircle2 className="h-4 w-4 text-verdict-green" /> : <AlertTriangle className="h-4 w-4 text-primary" />}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Key Dates */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Key Dates</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader><TableRow><TableHead>Date</TableHead><TableHead>Event</TableHead><TableHead>Source</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {facts.keyDates.map((d) => (
                <TableRow key={d.id}>
                  <TableCell>{d.date}</TableCell>
                  <TableCell>{d.event}</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{d.sourceDocName} p.{d.pageReference}</TableCell>
                  <TableCell>{d.confirmed ? <CheckCircle2 className="h-4 w-4 text-verdict-green" /> : <AlertTriangle className="h-4 w-4 text-primary" />}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Disputed Facts */}
      <Card className="bg-card border-border">
        <CardHeader><CardTitle className="text-lg font-sans">Disputed Facts</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {facts.disputedFacts.map((f) => (
              <div key={f.id} className="flex items-start gap-3 rounded-md bg-destructive/10 p-3 border border-destructive/20">
                <AlertTriangle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm">{f.description}</p>
                  <Badge variant="outline" className="mt-1">{f.status}</Badge>
                </div>
              </div>
            ))}
            {facts.disputedFacts.length === 0 && <p className="text-sm text-muted-foreground">No disputed facts.</p>}
          </div>
        </CardContent>
      </Card>

      {/* CTA */}
      {facts.allConfirmed && (
        <Button className="w-full bg-gradient-gold text-primary-foreground shadow-gold" asChild>
          <Link to={`/cases/${caseId}/witnesses`}>Case Is Ready — Add Witness</Link>
        </Button>
      )}
    </div>
  );
};

export default FactReviewPage;
