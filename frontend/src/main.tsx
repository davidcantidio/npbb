import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import "@fontsource-variable/roboto-flex";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Success from "./pages/Success";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import EventsList from "./pages/EventsList";
import EventDetail from "./pages/EventDetail";
import EventLeadFormConfig from "./pages/EventLeadFormConfig";
import NewEvent from "./pages/NewEvent";
import ComingSoon from "./pages/ComingSoon";
import { AuthProvider } from "./store/auth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";

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
        <Route path="/dashboard" element={<Navigate to="/success" replace />} />

        <Route path="/eventos" element={<EventsList />} />
        <Route path="/eventos/novo" element={<NewEvent />} />
        <Route path="/eventos/:id/editar" element={<NewEvent />} />
        <Route path="/eventos/:id" element={<EventDetail />} />
        <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />

        <Route path="/ativos" element={<ComingSoon title="Ativos" />} />
        <Route path="/leads" element={<ComingSoon title="Leads" />} />
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
