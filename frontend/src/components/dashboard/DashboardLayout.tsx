import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Box, Paper } from "@mui/material";
import { Outlet } from "react-router-dom";

import { DashboardSidebar } from "./DashboardSidebar";
import { DASHBOARD_MANIFEST } from "../../config/dashboardManifest";

/**
 * Renders the dashboard navigation inside the shared application sidebar slot.
 * Falls back to an inline sidebar only when the layout is mounted outside AppLayout.
 */
export default function DashboardLayout() {
  const [sidebarContainer, setSidebarContainer] = useState<HTMLElement | null>(null);
  const [sidebarInitialized, setSidebarInitialized] = useState(false);

  useEffect(() => {
    setSidebarContainer(document.getElementById("app-sidebar-slot"));
    setSidebarInitialized(true);
  }, []);

  const sidebar = <DashboardSidebar entries={DASHBOARD_MANIFEST} />;
  const sidebarPortal = sidebarContainer ? createPortal(sidebar, sidebarContainer) : null;

  return (
    <>
      {sidebarPortal}
      {!sidebarContainer && sidebarInitialized ? (
        <Paper variant="outlined" sx={{ mb: 3, p: 2 }}>
          {sidebar}
        </Paper>
      ) : null}
      <Box>
        <Outlet />
      </Box>
    </>
  );
}
