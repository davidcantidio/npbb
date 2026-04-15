import React, { Suspense, lazy } from "react";
import { Box, CircularProgress } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "../components/layout/AppLayout";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import AtivosList from "../pages/AtivosList";
import EventDetail from "../pages/EventDetail";
import IngressosPortal from "../pages/IngressosPortal";
import LegacyLeadStepRedirect from "../pages/leads/LegacyLeadStepRedirect";
import Login from "../pages/Login";
import Register from "../pages/Register";
import ResetPassword from "../pages/ResetPassword";
import Success from "../pages/Success";
import AppThemeShell from "../theme/AppThemeShell";

const DashboardHome = lazy(() => import("../pages/dashboard/DashboardHome"));
const EventAtivacoes = lazy(() => import("../pages/EventAtivacoes"));
const EventGamificacao = lazy(() => import("../pages/EventGamificacao"));
const EventLandingPage = lazy(() => import("../pages/EventLandingPage"));
const EventLeadFormConfig = lazy(() => import("../pages/EventLeadFormConfig"));
const EventQuestionario = lazy(() => import("../pages/EventQuestionario"));
const EventsList = lazy(() => import("../pages/EventsList"));
const LeadsAgeAnalysisPage = lazy(() => import("../pages/dashboard/LeadsAgeAnalysisPage"));
const LeadsImport = lazy(() => import("../pages/LeadsImport"));
const LeadsListPage = lazy(() => import("../pages/leads/LeadsListPage"));
const NewEvent = lazy(() => import("../pages/NewEvent"));
const EventSelectorPage = lazy(() => import("../pages/EventSelectorPage"));
const PatrocinadosPage = lazy(() => import("../features/patrocinados/PatrocinadosPage"));
const PatrocinadosEntryPage = lazy(() => import("../features/patrocinados/PatrocinadosEntryPage"));
const SponsoredPersonNewPage = lazy(() => import("../features/patrocinados/SponsoredPersonNewPage"));
const SponsoredInstitutionNewPage = lazy(() => import("../features/patrocinados/SponsoredInstitutionNewPage"));
const SponsorshipGroupNewPage = lazy(() => import("../features/patrocinados/SponsorshipGroupNewPage"));
const SponsoredPersonDetailPage = lazy(() => import("../features/patrocinados/SponsoredPersonDetailPage"));
const SponsoredInstitutionDetailPage = lazy(() => import("../features/patrocinados/SponsoredInstitutionDetailPage"));
const SponsorshipGroupPage = lazy(() => import("../features/patrocinados/SponsorshipGroupPage"));
const LegacySponsorshipGroupRedirect = lazy(
  () => import("../features/patrocinados/LegacySponsorshipGroupRedirect"),
);

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
      <Route element={<AppThemeShell />}>
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
          <Route
            path="/eventos/editar"
            element={withSuspense(<EventSelectorPage section="editar" />)}
          />
          <Route
            path="/eventos/formulario-lead"
            element={withSuspense(<EventSelectorPage section="formulario-lead" />)}
          />
          <Route
            path="/eventos/gamificacao"
            element={withSuspense(<EventSelectorPage section="gamificacao" />)}
          />
          <Route
            path="/eventos/ativacoes"
            element={withSuspense(<EventSelectorPage section="ativacoes" />)}
          />
          <Route
            path="/eventos/questionario"
            element={withSuspense(<EventSelectorPage section="questionario" />)}
          />
          <Route path="/eventos/:id/editar" element={withSuspense(<NewEvent />)} />
          <Route path="/eventos/:id/formulario-lead" element={withSuspense(<EventLeadFormConfig />)} />
          <Route path="/eventos/:id/gamificacao" element={withSuspense(<EventGamificacao />)} />
          <Route path="/eventos/:id/ativacoes" element={withSuspense(<EventAtivacoes />)} />
          <Route path="/eventos/:id/questionario" element={withSuspense(<EventQuestionario />)} />
          <Route path="/eventos/:id" element={<EventDetail />} />

          <Route path="/ativos" element={<AtivosList />} />
          <Route path="/ingressos" element={<IngressosPortal />} />
          <Route path="/leads" element={withSuspense(<LeadsListPage />)} />
          <Route path="/leads/importar" element={withSuspense(<LeadsImport />)} />
          <Route path="/leads/importacao-avancada" element={<Navigate to="/leads/importar" replace />} />
          <Route path="/leads/mapeamento" element={<LegacyLeadStepRedirect step="mapping" />} />
          <Route path="/leads/pipeline" element={<LegacyLeadStepRedirect step="pipeline" />} />
          <Route path="/patrocinados" element={withSuspense(<PatrocinadosPage />)} />
          <Route path="/patrocinados/novo" element={withSuspense(<PatrocinadosEntryPage />)} />
          <Route path="/patrocinados/pessoas/novo" element={withSuspense(<SponsoredPersonNewPage />)} />
          <Route path="/patrocinados/instituicoes/novo" element={withSuspense(<SponsoredInstitutionNewPage />)} />
          <Route path="/patrocinados/grupos/novo" element={withSuspense(<SponsorshipGroupNewPage />)} />
          <Route path="/patrocinados/pessoas/:id" element={withSuspense(<SponsoredPersonDetailPage />)} />
          <Route
            path="/patrocinados/instituicoes/:id"
            element={withSuspense(<SponsoredInstitutionDetailPage />)}
          />
          <Route path="/patrocinados/grupos/:id" element={withSuspense(<SponsorshipGroupPage />)} />
          <Route path="/patrocinados/:id" element={withSuspense(<LegacySponsorshipGroupRedirect />)} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
