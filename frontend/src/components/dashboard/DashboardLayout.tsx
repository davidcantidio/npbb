import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Box, Paper } from "@mui/material";
import { Outlet } from "react-router-dom";

import { DashboardSidebar } from "./DashboardSidebar";
import { DASHBOARD_MANIFEST } from "../../config/dashboardManifest";

const DASHBOARD_SIDEBAR_SLOT_ID = "app-sidebar-slot";

export default function DashboardLayout() {
  const [sidebarContainer, setSidebarContainer] = useState<HTMLElement | null>(null);
  const [sidebarReady, setSidebarReady] = useState(false);

  useEffect(() => {
    let animationFrameId = 0;
    let observer: MutationObserver | null = null;

    const bindSidebarContainer = () => {
      const nextContainer = document.getElementById(DASHBOARD_SIDEBAR_SLOT_ID);
      if (!nextContainer) return false;

      setSidebarContainer(nextContainer);
      setSidebarReady(true);
      observer?.disconnect();
      return true;
    };

    if (bindSidebarContainer()) {
      return () => undefined;
    }

    observer = new MutationObserver(() => {
      bindSidebarContainer();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    animationFrameId = window.requestAnimationFrame(() => {
      if (!bindSidebarContainer()) {
        setSidebarReady(true);
      }
    });

    return () => {
      window.cancelAnimationFrame(animationFrameId);
      observer?.disconnect();
    };
  }, []);

  const sidebar = <DashboardSidebar entries={DASHBOARD_MANIFEST} />;

  return (
    <>
      {sidebarContainer ? createPortal(sidebar, sidebarContainer) : null}
      {!sidebarContainer && sidebarReady ? (
        <Paper
          component="aside"
          aria-label="Sidebar do dashboard"
          variant="outlined"
          sx={{ mb: 3, borderRadius: 3, p: 2 }}
        >
          {sidebar}
        </Paper>
      ) : null}
      <Box component="section" aria-label="Conteudo do dashboard" sx={{ minWidth: 0 }}>
        <Outlet />
      </Box>
    </>
  );
}
