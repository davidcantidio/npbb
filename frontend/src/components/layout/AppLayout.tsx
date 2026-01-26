import { useEffect, useMemo, useState } from "react";
import {
  Avatar,
  AppBar,
  Box,
  Button,
  Divider,
  Drawer,
  Collapse,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import EventRoundedIcon from "@mui/icons-material/EventRounded";
import ConfirmationNumberRoundedIcon from "@mui/icons-material/ConfirmationNumberRounded";
import PeopleAltRoundedIcon from "@mui/icons-material/PeopleAltRounded";
import LocalOfferRoundedIcon from "@mui/icons-material/LocalOfferRounded";
import ExpandLessRoundedIcon from "@mui/icons-material/ExpandLessRounded";
import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../store/auth";

const DRAWER_WIDTH = 240;

type NavItem = {
  label: string;
  to: string;
  icon: React.ReactNode;
};

export default function AppLayout() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [eventsMenuOpen, setEventsMenuOpen] = useState(false);

  useEffect(() => {
    if (location.pathname.startsWith("/eventos")) {
      setEventsMenuOpen(true);
    }
  }, [location.pathname]);

  const navItems: NavItem[] = useMemo(
    () => [
      { label: "Dashboard", to: "/success", icon: <DashboardRoundedIcon /> },
      { label: "Eventos", to: "/eventos", icon: <EventRoundedIcon /> },
      { label: "Ativos", to: "/ativos", icon: <ConfirmationNumberRoundedIcon /> },
      { label: "Leads", to: "/leads", icon: <PeopleAltRoundedIcon /> },
      { label: "Cupons", to: "/cupons", icon: <LocalOfferRoundedIcon /> },
    ],
    [],
  );

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Toolbar sx={{ px: 2 }}>
        <Typography variant="subtitle1" fontWeight={900} letterSpacing={0.3}>
          Banco do Brasil
        </Typography>
      </Toolbar>
      <Divider />

      <List sx={{ flex: 1, py: 1 }}>
        {navItems.map((item) => {
          const selected =
            item.to === "/success"
              ? location.pathname === "/success" || location.pathname === "/dashboard"
              : location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);

          if (item.to === "/eventos") {
            return (
              <Box key={item.to}>
                <ListItemButton
                  selected={selected}
                  onClick={() => {
                    setEventsMenuOpen((prev) => !prev);
                    navigate(item.to);
                    setMobileOpen(false);
                  }}
                  sx={{
                    mx: 1,
                    borderRadius: 1,
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{ fontWeight: selected ? 800 : 600, fontSize: 13 }}
                  />
                  <Box sx={{ color: "text.secondary" }}>
                    {eventsMenuOpen ? (
                      <ExpandLessRoundedIcon fontSize="small" />
                    ) : (
                      <ExpandMoreRoundedIcon fontSize="small" />
                    )}
                  </Box>
                </ListItemButton>
                <Collapse in={eventsMenuOpen} timeout="auto">
                  <Box id="events-filters-slot" sx={{ px: 2, pb: 1 }} />
                </Collapse>
              </Box>
            );
          }

          return (
            <ListItemButton
              key={item.to}
              selected={selected}
              onClick={() => {
                navigate(item.to);
                setMobileOpen(false);
              }}
              sx={{
                mx: 1,
                borderRadius: 1,
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{ fontWeight: selected ? 800 : 600, fontSize: 13 }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block">
          Logado como
        </Typography>
        <Typography variant="body2" fontWeight={800} noWrap>
          {user?.email || "-"}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar
        position="fixed"
        color="transparent"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          borderBottom: 1,
          borderColor: "divider",
          backgroundColor: "rgba(246, 247, 251, 0.9)",
          backdropFilter: "blur(8px)",
          zIndex: (t) => t.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ gap: 1 }}>
          {!isDesktop && (
            <IconButton
              aria-label="Abrir menu"
              edge="start"
              onClick={() => setMobileOpen(true)}
              size="small"
            >
              <MenuRoundedIcon />
            </IconButton>
          )}
          <Typography variant="subtitle1" fontWeight={900} sx={{ flex: 1 }}>
            NPBB
          </Typography>
          <Button
            onClick={(e) => setUserMenuAnchor(e.currentTarget)}
            sx={{ textTransform: "none", fontWeight: 800, borderRadius: 2 }}
            color="inherit"
            startIcon={
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  bgcolor: "primary.main",
                  fontSize: 12,
                  fontWeight: 900,
                }}
              >
                {String(user?.email || "U")
                  .slice(0, 1)
                  .toUpperCase()}
              </Avatar>
            }
          >
            <Box sx={{ textAlign: "left", lineHeight: 1.1 }}>
              <Typography variant="body2" fontWeight={900} noWrap>
                {user?.email || "Usuário"}
              </Typography>
              {user?.tipo_usuario ? (
                <Typography variant="caption" color="text.secondary" noWrap>
                  {String(user.tipo_usuario).toLowerCase()}
                </Typography>
              ) : null}
            </Box>
          </Button>
          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={() => setUserMenuAnchor(null)}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem
              onClick={() => {
                setUserMenuAnchor(null);
                logout();
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <LogoutRoundedIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Sair" />
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant={isDesktop ? "permanent" : "temporary"}
        open={isDesktop ? true : mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
          },
        }}
      >
        {drawer}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, width: "100%" }}>
        <Toolbar />
        <Box sx={{ px: { xs: 2, md: 3 }, py: { xs: 2, md: 3 } }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
