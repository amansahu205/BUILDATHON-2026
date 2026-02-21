import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";

// Pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";
import DashboardPage from "./pages/DashboardPage";
import CaseListPage from "./pages/CaseListPage";
import NewCasePage from "./pages/NewCasePage";
import CaseDetailPage from "./pages/CaseDetailPage";
import DocumentsTab from "./pages/case-tabs/DocumentsTab";
import WitnessesTab from "./pages/case-tabs/WitnessesTab";
import SessionsTab from "./pages/case-tabs/SessionsTab";
import BriefsTab from "./pages/case-tabs/BriefsTab";
import FactReviewPage from "./pages/FactReviewPage";
import WitnessProfilePage from "./pages/WitnessProfilePage";
import SessionConfigPage from "./pages/SessionConfigPage";
import SessionLobbyPage from "./pages/SessionLobbyPage";
import LiveSessionPage from "./pages/LiveSessionPage";
import WitnessSessionPage from "./pages/WitnessSessionPage";
import PostSessionPage from "./pages/PostSessionPage";
import BriefViewerPage from "./pages/BriefViewerPage";
import SettingsPage from "./pages/SettingsPage";
import AdminPage from "./pages/AdminPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const AuthenticatedLayout = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute><AppShell>{children}</AppShell></ProtectedRoute>
);

const AdminLayout = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute requireAdmin><AppShell>{children}</AppShell></ProtectedRoute>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="/witness/session/:sessionId" element={<WitnessSessionPage />} />

            {/* Authenticated */}
            <Route path="/dashboard" element={<AuthenticatedLayout><DashboardPage /></AuthenticatedLayout>} />
            <Route path="/cases" element={<AuthenticatedLayout><CaseListPage /></AuthenticatedLayout>} />
            <Route path="/cases/new" element={<AuthenticatedLayout><NewCasePage /></AuthenticatedLayout>} />
            <Route path="/cases/:caseId" element={<AuthenticatedLayout><CaseDetailPage /></AuthenticatedLayout>}>
              <Route index element={<DocumentsTab />} />
              <Route path="witnesses" element={<WitnessesTab />} />
              <Route path="sessions" element={<SessionsTab />} />
              <Route path="briefs" element={<BriefsTab />} />
            </Route>
            <Route path="/cases/:caseId/documents/facts" element={<AuthenticatedLayout><FactReviewPage /></AuthenticatedLayout>} />
            <Route path="/cases/:caseId/witnesses/:witnessId" element={<AuthenticatedLayout><WitnessProfilePage /></AuthenticatedLayout>} />
            <Route path="/cases/:caseId/witnesses/:witnessId/session/new" element={<AuthenticatedLayout><SessionConfigPage /></AuthenticatedLayout>} />
            <Route path="/cases/:caseId/session/:sessionId/lobby" element={<AuthenticatedLayout><SessionLobbyPage /></AuthenticatedLayout>} />
            <Route path="/cases/:caseId/session/:sessionId/live" element={<LiveSessionPage />} />
            <Route path="/cases/:caseId/session/:sessionId/complete" element={<AuthenticatedLayout><PostSessionPage /></AuthenticatedLayout>} />
            <Route path="/briefs/:briefId" element={<AuthenticatedLayout><BriefViewerPage /></AuthenticatedLayout>} />
            <Route path="/settings" element={<AuthenticatedLayout><SettingsPage /></AuthenticatedLayout>} />

            {/* Admin */}
            <Route path="/admin" element={<AdminLayout><AdminPage /></AdminLayout>} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
