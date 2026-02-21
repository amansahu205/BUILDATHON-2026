import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, CartesianGrid } from "recharts";

// Static mockup data
const USERS = [
  { id: "1", name: "Sarah Chen", email: "schen@morrison.com", role: "admin", status: "active", sessions: 42 },
  { id: "2", name: "James Rivera", email: "jrivera@morrison.com", role: "attorney", status: "active", sessions: 28 },
  { id: "3", name: "Emily Watson", email: "ewatson@morrison.com", role: "attorney", status: "active", sessions: 15 },
  { id: "4", name: "Michael Park", email: "mpark@morrison.com", role: "attorney", status: "pending", sessions: 0 },
];

const ANALYTICS_DATA = [
  { month: "Sep", sessions: 12 },
  { month: "Oct", sessions: 18 },
  { month: "Nov", sessions: 24 },
  { month: "Dec", sessions: 31 },
  { month: "Jan", sessions: 28 },
  { month: "Feb", sessions: 35 },
];

const SCORE_DATA = [
  { name: "S. Chen", avgScore: 78, sessions: 42 },
  { name: "J. Rivera", avgScore: 72, sessions: 28 },
  { name: "E. Watson", avgScore: 65, sessions: 15 },
];

const AdminPage = () => {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-3xl font-bold">Firm Administration</h1>
        <Badge variant="outline" className="text-xs">Static Mockup</Badge>
      </div>

      <Tabs defaultValue="users">
        <TabsList><TabsTrigger value="users">Users</TabsTrigger><TabsTrigger value="security">Security</TabsTrigger><TabsTrigger value="analytics">Analytics</TabsTrigger></TabsList>

        <TabsContent value="users" className="mt-4">
          <Card className="bg-card border-border">
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow><TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead><TableHead>Sessions</TableHead></TableRow>
                </TableHeader>
                <TableBody>
                  {USERS.map(u => (
                    <TableRow key={u.id}>
                      <TableCell className="font-medium">{u.name}</TableCell>
                      <TableCell className="text-muted-foreground">{u.email}</TableCell>
                      <TableCell><Badge variant="secondary" className="capitalize">{u.role}</Badge></TableCell>
                      <TableCell><Badge variant={u.status === "active" ? "default" : "outline"} className="capitalize">{u.status}</Badge></TableCell>
                      <TableCell>{u.sessions}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-4">
          <Card className="bg-card border-border">
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-center justify-between"><Label>Data Retention Period</Label><span className="text-sm font-medium">90 days</span></div>
              <div className="flex items-center justify-between"><Label>SSO Configuration</Label><Badge variant="default">Enabled</Badge></div>
              <div className="flex items-center justify-between"><Label>Case Isolation</Label><Switch checked={true} disabled /></div>
              <div className="flex items-center justify-between"><Label>Behavioral Sentinel</Label><Switch checked={false} disabled /></div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="mt-4 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-card border-border"><CardContent className="pt-6 text-center"><p className="text-3xl font-bold">148</p><p className="text-sm text-muted-foreground">Total Sessions</p></CardContent></Card>
            <Card className="bg-card border-border"><CardContent className="pt-6 text-center"><p className="text-3xl font-bold">12</p><p className="text-sm text-muted-foreground">Witnesses Prepped</p></CardContent></Card>
            <Card className="bg-card border-border"><CardContent className="pt-6 text-center"><p className="text-3xl font-bold text-verdict-green">72</p><p className="text-sm text-muted-foreground">Avg Score</p></CardContent></Card>
          </div>

          <Card className="bg-card border-border">
            <CardHeader><CardTitle className="text-base font-sans">Sessions by Month</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ANALYTICS_DATA}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 30% 18%)" />
                  <XAxis dataKey="month" tick={{ fill: "hsl(215 20% 55%)", fontSize: 12 }} />
                  <YAxis tick={{ fill: "hsl(215 20% 55%)", fontSize: 12 }} />
                  <Bar dataKey="sessions" fill="hsl(38 92% 50%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader><CardTitle className="text-base font-sans">Average Score by Attorney</CardTitle></CardHeader>
            <CardContent>
              <Table>
                <TableHeader><TableRow><TableHead>Attorney</TableHead><TableHead>Avg Score</TableHead><TableHead>Sessions</TableHead></TableRow></TableHeader>
                <TableBody>
                  {SCORE_DATA.map(s => (
                    <TableRow key={s.name}>
                      <TableCell className="font-medium">{s.name}</TableCell>
                      <TableCell className={s.avgScore >= 70 ? "text-verdict-green font-bold" : "text-primary font-bold"}>{s.avgScore}</TableCell>
                      <TableCell>{s.sessions}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminPage;
