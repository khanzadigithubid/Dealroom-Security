import { Navigate, Route, Routes } from "react-router-dom";
import { getToken } from "./api";
import AppShell from "./components/AppShell";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import ControlsPage from "./pages/ControlsPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import QuestionnairesPage from "./pages/QuestionnairesPage";
import QuestionnaireDetail from "./pages/QuestionnaireDetail";
import TrustPage from "./pages/TrustPage";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return <AppShell>{children}</AppShell>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route path="/trust/:slug" element={<TrustPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/integrations"
        element={
          <PrivateRoute>
            <IntegrationsPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/controls"
        element={
          <PrivateRoute>
            <ControlsPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/questionnaires"
        element={
          <PrivateRoute>
            <QuestionnairesPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/questionnaires/:id"
        element={
          <PrivateRoute>
            <QuestionnaireDetail />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
