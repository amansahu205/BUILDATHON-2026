import React from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { casesService } from "@/services/cases";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { differenceInDays, parseISO } from "date-fns";
import { CASE_TYPE_LABELS } from "@/types";

interface CaseLayoutProps {
  children: React.ReactNode;
}

const TABS = [
  { label: "Documents", path: "" },
  { label: "Witnesses", path: "/witnesses" },
  { label: "Sessions", path: "/sessions" },
  { label: "Briefs", path: "/briefs" },
];

export const CaseLayout: React.FC<CaseLayoutProps> = ({ children }) => {
  const { caseId } = useParams<{ caseId: string }>();
  const location = useLocation();

  const { data: caseData, isLoading } = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => casesService.get(caseId!),
    enabled: !!caseId,
  });

  const getCountdownBadge = () => {
    if (!caseData?.depositionDate) return null;
    const days = differenceInDays(parseISO(caseData.depositionDate), new Date());
    const variant = days <= 3 ? "destructive" : days <= 7 ? "default" : "secondary";
    return (
      <Badge variant={variant} className={cn(days <= 3 && "animate-pulse-gold")}>
        {days <= 0 ? "Today" : `${days}d to deposition`}
      </Badge>
    );
  };

  const basePath = `/cases/${caseId}`;

  const getActiveTab = () => {
    const relative = location.pathname.replace(basePath, "");
    if (relative.startsWith("/witnesses")) return "/witnesses";
    if (relative.startsWith("/sessions")) return "/sessions";
    if (relative.startsWith("/briefs")) return "/briefs";
    return "";
  };

  return (
    <div className="flex flex-col">
      {/* Case Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-4 w-40" />
          </div>
        ) : caseData ? (
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-display font-bold text-foreground">{caseData.name}</h1>
              <p className="text-sm text-muted-foreground mt-1">
                {CASE_TYPE_LABELS[caseData.caseType]}
                {caseData.opposingFirm && ` • vs. ${caseData.opposingFirm}`}
              </p>
            </div>
            {getCountdownBadge()}
          </div>
        ) : (
          <p className="text-muted-foreground">Case not found</p>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-border bg-card px-6">
        <nav className="flex gap-0">
          {TABS.map((tab) => {
            const isActive = getActiveTab() === tab.path;
            return (
              <Link
                key={tab.path}
                to={`${basePath}${tab.path}`}
                className={cn(
                  "relative px-4 py-3 text-sm font-medium transition-colors",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {tab.label}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 p-6">{children}</div>
    </div>
  );
};
