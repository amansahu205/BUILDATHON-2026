import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsService } from "@/services/settings";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { Trash2 } from "lucide-react";

const SettingsPage = () => {
  const queryClient = useQueryClient();
  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: settingsService.get,
  });

  const { data: activeSessions } = useQuery({
    queryKey: ["active-sessions"],
    queryFn: settingsService.getActiveSessions,
  });

  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");

  const changePw = useMutation({
    mutationFn: () => settingsService.changePassword(currentPw, newPw),
    onSuccess: () => { setCurrentPw(""); setNewPw(""); },
  });

  const revokeSession = useMutation({
    mutationFn: (id: string) => settingsService.revokeSession(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["active-sessions"] }),
  });

  if (isLoading) return <div className="p-6 space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-32 rounded-lg" />)}</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="font-display text-3xl font-bold mb-6">Settings</h1>
      <Tabs defaultValue="profile">
        <TabsList><TabsTrigger value="profile">Profile</TabsTrigger><TabsTrigger value="session">Session Defaults</TabsTrigger><TabsTrigger value="notifications">Notifications</TabsTrigger><TabsTrigger value="security">Security</TabsTrigger></TabsList>

        <TabsContent value="profile">
          <Card className="bg-card border-border mt-4">
            <CardContent className="pt-6 space-y-4">
              <div className="space-y-2"><Label>Name</Label><Input defaultValue={settings?.profile.name} /></div>
              <div className="space-y-2"><Label>Email</Label><Input defaultValue={settings?.profile.email} disabled={settings?.profile.ssoManaged} /></div>
              <div className="space-y-2"><Label>Title</Label><Input defaultValue={settings?.profile.title} /></div>
              <div className="space-y-2"><Label>Practice Area</Label><Input defaultValue={settings?.profile.practiceArea} /></div>
              <Button className="bg-gradient-gold text-primary-foreground">Save</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="session">
          <Card className="bg-card border-border mt-4">
            <CardContent className="pt-6 space-y-4">
              <div className="space-y-2">
                <Label>Default Duration</Label>
                <Select defaultValue={String(settings?.sessionDefaults.durationMinutes || 30)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="15">15 min</SelectItem><SelectItem value="30">30 min</SelectItem><SelectItem value="45">45 min</SelectItem><SelectItem value="60">60 min</SelectItem></SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Default Aggression</Label>
                <Select defaultValue={settings?.sessionDefaults.aggressionLevel || "standard"}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="standard">Standard</SelectItem><SelectItem value="elevated">Elevated</SelectItem><SelectItem value="high_stakes">High-Stakes</SelectItem></SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between"><Label>Objection Copilot Default</Label><Switch defaultChecked={settings?.sessionDefaults.objectionCopilotDefault} /></div>
              <Button className="bg-gradient-gold text-primary-foreground">Save</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card className="bg-card border-border mt-4">
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-center justify-between"><Label>Brief Ready</Label><Switch defaultChecked={settings?.notifications.briefReady} /></div>
              <div className="flex items-center justify-between"><Label>Plateau Alert</Label><Switch defaultChecked={settings?.notifications.plateauAlert} /></div>
              <div className="flex items-center justify-between"><Label>Session Reminder</Label><Switch defaultChecked={settings?.notifications.sessionReminder} /></div>
              <Button className="bg-gradient-gold text-primary-foreground">Save</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <div className="space-y-4 mt-4">
            <Card className="bg-card border-border">
              <CardHeader><CardTitle className="text-base font-sans">Change Password</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2"><Label>Current Password</Label><Input type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)} /></div>
                <div className="space-y-2"><Label>New Password</Label><Input type="password" value={newPw} onChange={e => setNewPw(e.target.value)} /></div>
                <Button variant="outline" onClick={() => changePw.mutate()} disabled={changePw.isPending}>Update Password</Button>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardHeader><CardTitle className="text-base font-sans">Active Sessions</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {activeSessions?.map(s => (
                  <div key={s.id} className="flex items-center justify-between rounded bg-muted/50 px-4 py-3">
                    <div>
                      <p className="text-sm font-medium">{s.device}</p>
                      <p className="text-xs text-muted-foreground">{s.ipAddress} • {s.lastActive}</p>
                    </div>
                    {s.current ? <Badge variant="secondary">Current</Badge> : (
                      <Button variant="ghost" size="sm" onClick={() => revokeSession.mutate(s.id)}><Trash2 className="h-3 w-3 text-destructive" /></Button>
                    )}
                  </div>
                ))}
                {!activeSessions?.length && <p className="text-sm text-muted-foreground">No active sessions data.</p>}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
