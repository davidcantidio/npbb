import React from "react";
import ReactDOM from "react-dom/client";
import "@fontsource-variable/roboto-flex";
import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./app/AppRoutes";
import { AuthProvider } from "./store/auth";
import { ThemeModeProvider } from "./theme/ThemeModeProvider";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <ThemeModeProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeModeProvider>
    </AuthProvider>
  </React.StrictMode>,
);
