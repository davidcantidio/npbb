import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider, createTheme, CssBaseline, Box, CircularProgress } from "@mui/material";
import "@fontsource-variable/roboto-flex";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Success from "./pages/Success";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import EventDetail from "./pages/EventDetail";
import ComingSoon from "./pages/ComingSoon";
import AtivosList from "./pages/AtivosList";
import IngressosPortal from "./pages/IngressosPortal";
import PublicidadeImport from "./pages/PublicidadeImport";
import DashboardLeads from "./pages/DashboardLeads";
import { AuthProvider } from "./store/auth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";

const EventsList = lazy(() => import("./pages/EventsList"));
const NewEvent = lazy(() => import("./pages/NewEvent"));
const EventLeadFormConfig = lazy(() => import("./pages/EventLeadFormConfig"));
const EventGamificacao = lazy(() => import("./pages/EventGamificacao"));
const EventAtivacoes = lazy(() => import("./pages/EventAtivacoes"));
const EventQuestionario = lazy(() => import("./pages/EventQuestionario"));
const LeadsImport = lazy(() => import("./pages/LeadsImport"));

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#6750A4",
    },
    secondary: {
      main: "#625B71",
    },
    background: {
      default: "#f6f7fb",
      paper: "#ffffff",
    },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Roboto Flex Variable", "Roboto", "Inter", system-ui, -apple-system, sans-serif',
    fontSize: 13,
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 700,
  },
  components: {
    MuiTextField: { defaultProps: { size: "small" } },
    MuiAutocomplete: { defaultProps: { size: "small" } },
    MuiSelect: { defaultProps: { size: "small" } },
    MuiFormControl: { defaultProps: { size: "small" } },
    MuiChip: { defaultProps: { size: "small" } },
  },
});

function AppRoutes() {
  const withSuspense = (element: React.ReactNode) => (
    <Suspense
      fallback={
        <Box sx={{ py: 8, display: "flex", justifyContent: "center" }}>
          <CircularProgress size={28} />
        </Box>
      }
    >
      {element}
    </Suspense>
  );

  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/novo-usuario" element={<Register />} />
      <Route path="/register" element={<Navigate to="/novo-usuario" replace />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/success" element={<Success />} />
        <Route path="/dashboard" element={<Navigate to="/dashboard/leads" replace />} />
        <Route path="/dashboard/leads" element={<DashboardLeads />} />

        <Route path="/eventos" element={withSuspense(<EventsList />)} />
        <Route path="/eventos/novo" element={withSuspense(<NewEvent />)} />
        <Route path="/eventos/:id/editar" element={withSuspense(<NewEvent />)} />
        <Route path="/eventos/:id/formulario-lead" element={withSuspense(<EventLeadFormConfig />)} />
        <Route path="/eventos/:id/gamificacao" element={withSuspense(<EventGamificacao />)} />
        <Route path="/eventos/:id/ativacoes" element={withSuspense(<EventAtivacoes />)} />
        <Route path="/eventos/:id/questionario" element={withSuspense(<EventQuestionario />)} />
        <Route path="/eventos/:id" element={<EventDetail />} />

        <Route path="/ativos" element={<AtivosList />} />
        <Route path="/ingressos" element={<IngressosPortal />} />
        <Route path="/leads" element={withSuspense(<LeadsImport />)} />
        <Route path="/publicidade" element={<PublicidadeImport />} />
        <Route path="/cupons" element={<ComingSoon title="Cupons" />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </AuthProvider>
  </React.StrictMode>,
);
