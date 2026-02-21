import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { casesService } from "@/services/cases";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import type { CaseType, CreateCaseRequest } from "@/types";
import { CASE_TYPE_LABELS } from "@/types";

const NewCasePage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [caseType, setCaseType] = useState<CaseType | "">("");
  const [opposingFirm, setOpposingFirm] = useState("");
  const [date, setDate] = useState<Date>();

  const create = useMutation({
    mutationFn: (payload: CreateCaseRequest) => casesService.create(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      navigate(`/cases/${data.id}`);
    },
  });

  const isValid = name.length >= 3 && name.length <= 120 && caseType && date;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || !caseType || !date) return;
    create.mutate({ name, caseType: caseType as CaseType, opposingFirm: opposingFirm || undefined, depositionDate: date.toISOString() });
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="font-display text-2xl">New Case</CardTitle>
          <CardDescription>Set up a new case for deposition preparation.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="name">Case Name *</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Smith v. Memorial Hospital" maxLength={120} />
              {name.length > 0 && name.length < 3 && <p className="text-xs text-destructive">Name must be at least 3 characters</p>}
            </div>

            <div className="space-y-2">
              <Label>Case Type *</Label>
              <Select value={caseType} onValueChange={(v) => setCaseType(v as CaseType)}>
                <SelectTrigger><SelectValue placeholder="Select case type" /></SelectTrigger>
                <SelectContent>
                  {Object.entries(CASE_TYPE_LABELS).map(([k, v]) => (
                    <SelectItem key={k} value={k}>{v}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="opposing">Opposing Firm (optional)</Label>
              <Input id="opposing" value={opposingFirm} onChange={(e) => setOpposingFirm(e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label>Deposition Date *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}>
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0"><Calendar mode="single" selected={date} onSelect={setDate} /></PopoverContent>
              </Popover>
            </div>

            {create.error && <p className="text-sm text-destructive">Failed to create case. Please try again.</p>}

            <div className="flex gap-3 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>Cancel</Button>
              <Button type="submit" className="bg-gradient-gold text-primary-foreground flex-1" disabled={!isValid || create.isPending}>
                {create.isPending ? "Creating…" : "Create Case"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default NewCasePage;
