import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { casesService } from "@/services/cases";
import { useAuthContext } from "@/contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Briefcase, Calendar, TrendingUp } from "lucide-react";
import { differenceInDays, parseISO, format } from "date-fns";
import { CASE_TYPE_LABELS } from "@/types";

const DashboardPage = () => {
  const { user } = useAuthContext();
  const { data: casesData, isLoading } = useQuery({
    queryKey: ["cases", { page: 1 }],
    queryFn: () => casesService.list({ page: 1 }),
  });

  const cases = casesData?.data || [];

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Welcome back{user ? `, ${user.name.split(" ")[0]}` : ""}</p>
        </div>
        <Button className="bg-gradient-gold text-primary-foreground shadow-gold" asChild>
          <Link to="/cases/new"><Plus className="mr-2 h-4 w-4" /> New Case</Link>
        </Button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: Briefcase, label: "Active Cases", value: cases.length },
          { icon: Calendar, label: "Upcoming Depositions", value: cases.filter(c => differenceInDays(parseISO(c.depositionDate), new Date()) <= 14).length },
          { icon: TrendingUp, label: "Sessions This Month", value: "—" },
        ].map((stat) => (
          <Card key={stat.label} className="bg-card border-border">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <stat.icon className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Active Cases */}
      <div>
        <h2 className="font-display text-xl font-semibold mb-4">Active Cases</h2>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-40 rounded-lg" />)}
          </div>
        ) : cases.length === 0 ? (
          <Card className="bg-card border-border border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Briefcase className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">Create your first case</p>
              <p className="text-sm text-muted-foreground mb-4">Get started by setting up a new case for deposition prep.</p>
              <Button className="bg-gradient-gold text-primary-foreground" asChild>
                <Link to="/cases/new"><Plus className="mr-2 h-4 w-4" /> New Case</Link>
              </Button>
            </CardContent>
          </Card>
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
                        <span>{c.sessionCount} sessions</span>
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
    </div>
  );
};

export default DashboardPage;
