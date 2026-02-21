import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { authService } from "@/services/auth";
import { Scale, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { FirmOnboardingPayload, SeatProvision } from "@/types";

const STEPS = ["Firm Configuration", "Seat Provisioning", "Security Settings"];

const OnboardingPage = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [step, setStep] = useState(0);

  // Form state
  const [firmName, setFirmName] = useState("");
  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [ssoEnabled, setSsoEnabled] = useState(false);
  const [seats, setSeats] = useState<SeatProvision[]>([]);
  const [seatEmail, setSeatEmail] = useState("");
  const [seatName, setSeatName] = useState("");
  const [seatRole, setSeatRole] = useState<"attorney" | "admin">("attorney");
  const [retentionDays, setRetentionDays] = useState(90);
  const [caseIsolation, setCaseIsolation] = useState(true);
  const [behavioralSentinel, setBehavioralSentinel] = useState(false);

  const { data: tokenData, isLoading: validating, error: tokenError } = useQuery({
    queryKey: ["onboarding-token", token],
    queryFn: () => authService.validateOnboardingToken(token),
    enabled: !!token,
  });

  const complete = useMutation({
    mutationFn: () => {
      const payload: FirmOnboardingPayload = {
        firmName, adminName, adminEmail, ssoEnabled, seats,
        retentionDays, caseIsolation, behavioralSentinel,
      };
      return authService.completeOnboarding(token, payload);
    },
    onSuccess: () => {
      window.location.href = "/dashboard";
    },
  });

  const addSeat = () => {
    if (seatEmail && seatName) {
      setSeats([...seats, { email: seatEmail, name: seatName, role: seatRole }]);
      setSeatEmail("");
      setSeatName("");
    }
  };

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Card className="w-full max-w-md"><CardContent className="pt-6 text-center text-destructive">Invalid or missing onboarding token.</CardContent></Card>
      </div>
    );
  }

  if (validating) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Skeleton className="h-64 w-96" />
      </div>
    );
  }

  if (tokenError) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Card className="w-full max-w-md"><CardContent className="pt-6 text-center text-destructive">Token expired or invalid. Please request a new onboarding link.</CardContent></Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Scale className="h-8 w-8 text-primary" />
          <span className="font-display text-2xl font-bold text-gradient-gold">VERDICT</span>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {STEPS.map((s, i) => (
            <React.Fragment key={s}>
              <div className={`flex items-center justify-center h-8 w-8 rounded-full text-xs font-bold ${i <= step ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                {i < step ? <Check className="h-4 w-4" /> : i + 1}
              </div>
              {i < STEPS.length - 1 && <div className={`h-0.5 w-12 ${i < step ? "bg-primary" : "bg-muted"}`} />}
            </React.Fragment>
          ))}
        </div>
        <p className="text-center text-sm text-muted-foreground mb-6">{STEPS[step]}</p>

        <Card className="border-border bg-card">
          <CardContent className="pt-6 space-y-4">
            {step === 0 && (
              <>
                <div className="space-y-2"><Label>Firm Name</Label><Input value={firmName} onChange={(e) => setFirmName(e.target.value)} placeholder="e.g. Morrison & Associates" /></div>
                <div className="space-y-2"><Label>Admin Name</Label><Input value={adminName} onChange={(e) => setAdminName(e.target.value)} /></div>
                <div className="space-y-2"><Label>Admin Email</Label><Input value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} type="email" /></div>
                <div className="flex items-center justify-between"><Label>Enable SSO</Label><Switch checked={ssoEnabled} onCheckedChange={setSsoEnabled} /></div>
              </>
            )}
            {step === 1 && (
              <>
                <div className="grid grid-cols-3 gap-2">
                  <Input placeholder="Name" value={seatName} onChange={(e) => setSeatName(e.target.value)} />
                  <Input placeholder="Email" value={seatEmail} onChange={(e) => setSeatEmail(e.target.value)} />
                  <div className="flex gap-2">
                    <Select value={seatRole} onValueChange={(v) => setSeatRole(v as "attorney" | "admin")}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent><SelectItem value="attorney">Attorney</SelectItem><SelectItem value="admin">Admin</SelectItem></SelectContent>
                    </Select>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={addSeat}>+ Add Seat</Button>
                {seats.length > 0 && (
                  <div className="space-y-1 text-sm">{seats.map((s, i) => (
                    <div key={i} className="flex items-center justify-between rounded bg-muted px-3 py-2">
                      <span>{s.name} ({s.email})</span><span className="text-xs text-muted-foreground capitalize">{s.role}</span>
                    </div>
                  ))}</div>
                )}
              </>
            )}
            {step === 2 && (
              <>
                <div className="space-y-2"><Label>Data Retention (days)</Label><Input type="number" value={retentionDays} onChange={(e) => setRetentionDays(Number(e.target.value))} /></div>
                <div className="flex items-center justify-between"><Label>Case Isolation</Label><Switch checked={caseIsolation} onCheckedChange={setCaseIsolation} /></div>
                <div className="flex items-center justify-between"><Label>Behavioral Sentinel</Label><Switch checked={behavioralSentinel} onCheckedChange={setBehavioralSentinel} /></div>
              </>
            )}

            <div className="flex justify-between pt-4">
              {step > 0 && <Button variant="outline" onClick={() => setStep(step - 1)}>Back</Button>}
              {step < 2 ? (
                <Button className="ml-auto bg-gradient-gold text-primary-foreground" onClick={() => setStep(step + 1)}>Continue</Button>
              ) : (
                <Button className="ml-auto bg-gradient-gold text-primary-foreground" onClick={() => complete.mutate()} disabled={complete.isPending}>
                  {complete.isPending ? "Setting up…" : "Complete Setup"}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OnboardingPage;
