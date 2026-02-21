import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { witnessesService } from "@/services/witnesses";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, User } from "lucide-react";
import { useState } from "react";

const WitnessesTab = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("");

  const { data: witnesses, isLoading } = useQuery({
    queryKey: ["witnesses", caseId],
    queryFn: () => witnessesService.list(caseId!),
    enabled: !!caseId,
  });

  const create = useMutation({
    mutationFn: () => witnessesService.create(caseId!, { name, role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["witnesses", caseId] });
      setOpen(false);
      setName("");
      setRole("");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-gold text-primary-foreground"><Plus className="mr-2 h-4 w-4" /> Add Witness</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Witness</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2"><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Dr. Sarah Chen" /></div>
              <div className="space-y-2"><Label>Role</Label><Input value={role} onChange={(e) => setRole(e.target.value)} placeholder="e.g. Treating Physician" /></div>
              <Button className="w-full bg-gradient-gold text-primary-foreground" disabled={!name || create.isPending} onClick={() => create.mutate()}>
                {create.isPending ? "Adding…" : "Add Witness"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{[1, 2].map((i) => <Skeleton key={i} className="h-28 rounded-lg" />)}</div>
      ) : !witnesses?.length ? (
        <p className="text-center text-muted-foreground py-8">No witnesses added yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {witnesses.map((w) => (
            <Link key={w.id} to={`/cases/${caseId}/witnesses/${w.id}`}>
              <Card className="bg-card border-border hover:border-primary/30 transition-colors cursor-pointer">
                <CardContent className="flex items-center gap-4 py-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10"><User className="h-5 w-5 text-primary" /></div>
                  <div className="flex-1">
                    <p className="font-medium">{w.name}</p>
                    <p className="text-xs text-muted-foreground">{w.role}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{w.sessionCount} sessions</p>
                    {w.latestScore != null && <Badge variant={w.latestScore >= 70 ? "default" : "destructive"}>{w.latestScore}</Badge>}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default WitnessesTab;
