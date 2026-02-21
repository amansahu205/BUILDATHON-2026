import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { casesService } from "@/services/cases";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, AlertCircle, CheckCircle2 } from "lucide-react";
import { useCallback, useState } from "react";
import type { DocumentStatus } from "@/types";

const STATUS_CONFIG: Record<DocumentStatus, { icon: React.ElementType; color: string; label: string }> = {
  uploading: { icon: Upload, color: "text-verdict-blue", label: "Uploading" },
  indexing: { icon: FileText, color: "text-primary", label: "Indexing" },
  ready: { icon: CheckCircle2, color: "text-verdict-green", label: "Ready" },
  failed: { icon: AlertCircle, color: "text-destructive", label: "Failed" },
};

const DocumentsTab = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const { data: docs, isLoading } = useQuery({
    queryKey: ["documents", caseId],
    queryFn: () => casesService.getDocuments(caseId!),
    enabled: !!caseId,
  });

  const upload = useMutation({
    mutationFn: ({ file }: { file: File }) =>
      casesService.uploadDocument(caseId!, file, "other", (pct) => {
        setUploadProgress((p) => ({ ...p, [file.name]: pct }));
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", caseId] });
    },
  });

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    files.forEach((file) => upload.mutate({ file }));
  }, [upload]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    files.forEach((file) => upload.mutate({ file }));
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors"
      >
        <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
        <p className="text-sm text-muted-foreground mb-2">Drag & drop documents here, or</p>
        <label>
          <Button variant="outline" size="sm" asChild><span>Browse Files</span></Button>
          <input type="file" multiple className="hidden" onChange={handleFileSelect} />
        </label>
      </div>

      {/* Upload progress */}
      {Object.entries(uploadProgress).map(([name, pct]) => (
        pct < 100 && (
          <div key={name} className="flex items-center gap-3">
            <span className="text-sm truncate flex-1">{name}</span>
            <Progress value={pct} className="w-32" />
            <span className="text-xs text-muted-foreground">{pct}%</span>
          </div>
        )
      ))}

      {/* Documents */}
      {isLoading ? (
        <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 rounded-lg" />)}</div>
      ) : !docs?.length ? (
        <p className="text-center text-muted-foreground py-8">No documents uploaded yet.</p>
      ) : (
        <div className="space-y-3">
          {docs.map((doc) => {
            const cfg = STATUS_CONFIG[doc.status];
            return (
              <Card key={doc.id} className="bg-card border-border">
                <CardContent className="flex items-center gap-4 py-4">
                  <cfg.icon className={`h-5 w-5 shrink-0 ${cfg.color}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{doc.fileName}</p>
                    <p className="text-xs text-muted-foreground">{(doc.fileSize / 1024 / 1024).toFixed(1)} MB{doc.pageCount ? ` • ${doc.pageCount} pages` : ""}</p>
                  </div>
                  <Badge variant="outline" className="shrink-0">{cfg.label}</Badge>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DocumentsTab;
