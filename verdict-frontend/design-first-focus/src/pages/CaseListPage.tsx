import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { casesService } from "@/services/cases";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { differenceInDays, parseISO, format } from "date-fns";
import { CASE_TYPE_LABELS } from "@/types";

const CaseListPage = () => {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["cases", { search }],
    queryFn: () => casesService.list({ search: search || undefined }),
  });

  const cases = data?.data || [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl font-bold">Cases</h1>
        <Button className="bg-gradient-gold text-primary-foreground shadow-gold" asChild>
          <Link to="/cases/new"><Plus className="mr-2 h-4 w-4" /> New Case</Link>
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Search cases…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => <Skeleton key={i} className="h-40 rounded-lg" />)}
        </div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <p>No cases found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases.map((c) => {
            const days = differenceInDays(parseISO(c.depositionDate), new Date());
            return (
              <Link key={c.id} to={`/cases/${c.id}`}>
                <Card className="bg-card border-border hover:border-primary/30 transition-colors cursor-pointer h-full">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg font-sans">{c.name}</CardTitle>
                      <Badge variant={days <= 3 ? "destructive" : days <= 7 ? "default" : "secondary"}>
                        {days <= 0 ? "Today" : `${days}d`}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-3">{CASE_TYPE_LABELS[c.caseType]}</p>
                    <div className="flex gap-4 text-xs text-muted-foreground">
                      <span>{c.witnessCount} witnesses</span>
                      <span>{c.documentCount} docs</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      Deposition: {format(parseISO(c.depositionDate), "MMM d, yyyy")}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CaseListPage;
