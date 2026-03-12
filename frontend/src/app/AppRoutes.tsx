import React, { Suspense, lazy } from "react";
import { Box, CircularProgress } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "../components/layout/AppLayout";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import AtivosList from "../pages/AtivosList";
import ComingSoon from "../pages/ComingSoon";
import EventDetail from "../pages/EventDetail";
import IngressosPortal from "../pages/IngressosPortal";
import Login from "../pages/Login";
import PublicidadeImport from "../pages/PublicidadeImport";
import Register from "../pages/Register";
import ResetPassword from "../pages/ResetPassword";
import Success from "../pages/Success";

const DashboardHome = lazy(() => import("../pages/dashboard/DashboardHome"));
const EventAtivacoes = lazy(() => import("../pages/EventAtivacoes"));
const EventGamificacao = lazy(() => import("../pages/EventGamificacao"));
const EventLandingPage = lazy(() => import("../pages/EventLandingPage"));
const EventLeadFormConfig = lazy(() => import("../pages/EventLeadFormConfig"));
const EventQuestionario = lazy(() => import("../pages/EventQuestionario"));
const EventsList = lazy(() => import("../pages/EventsList"));
const LeadsAgeAnalysisPage = lazy(() => import("../pages/dashboard/LeadsAgeAnalysisPage"));
const LeadsImport = lazy(() => import("../pages/LeadsImport"));
const MapeamentoPage = lazy(() => import("../pages/leads/MapeamentoPage"));
const NewEvent = lazy(() => import("../pages/NewEvent"));
const PipelineStatusPage = lazy(() => import("../pages/leads/PipelineStatusPage"));

export default function AppRoutes() {
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
      <Route
        path="/eventos/:evento_id/ativacoes/:ativacao_id"
        element={withSuspense(<EventLandingPage />)}
      />
      <Route path="/landing/eventos/:eventId" element={withSuspense(<EventLandingPage />)} />
      <Route path="/landing/ativacoes/:ativacaoId" element={withSuspense(<EventLandingPage />)} />
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

        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={withSuspense(<DashboardHome />)} />
          <Route path="leads" element={<Navigate to="analise-etaria" replace />} />
          <Route path="leads/analise-etaria" element={withSuspense(<LeadsAgeAnalysisPage />)} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>

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
        <Route path="/leads" element={<Navigate to="/leads/importar" replace />} />
        <Route path="/leads/importar" element={withSuspense(<LeadsImport />)} />
        <Route path="/leads/importacao-avancada" element={<Navigate to="/leads/importar" replace />} />
        <Route path="/leads/mapeamento" element={withSuspense(<MapeamentoPage />)} />
        <Route path="/leads/pipeline" element={withSuspense(<PipelineStatusPage />)} />
        <Route path="/publicidade" element={<PublicidadeImport />} />
        <Route path="/cupons" element={<ComingSoon title="Cupons" />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
