import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import "@fontsource-variable/roboto-flex";
import Login from "./pages/Login";
import Success from "./pages/Success";
import Register from "./pages/Register";
import { AuthProvider } from "./store/auth";
import { ProtectedRoute } from "./components/ProtectedRoute";

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
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 700,
  },
});

const path = window.location.pathname;
let Screen: React.ReactNode;
if (path === "/success" || path === "/dashboard") {
  Screen = (
    <ProtectedRoute>
      <Success />
    </ProtectedRoute>
  );
} else if (path === "/register") {
  Screen = <Register />;
} else {
  Screen = <Login />;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {Screen}
      </ThemeProvider>
    </AuthProvider>
  </React.StrictMode>,
);
