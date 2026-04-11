import { useMemo, useState } from "react";
import {
  Avatar,
  AppBar,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
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
import CampaignRoundedIcon from "@mui/icons-material/CampaignRounded";
import VolunteerActivismRoundedIcon from "@mui/icons-material/VolunteerActivismRounded";
import TuneRoundedIcon from "@mui/icons-material/TuneRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../store/auth";
import { useThemeMode } from "../../theme/ThemeModeProvider";

const DRAWER_WIDTH = 240;

type NavSubItem = {
  label: string;
  to: string;
  icon: React.ReactNode;
};

type NavItem = {
  label: string;
  to?: string;
  icon: React.ReactNode;
  children?: NavSubItem[];
};

const ATIVOS_SUBMENU: NavSubItem[] = [
  { label: "Dashboard", to: "/ativos", icon: <DashboardRoundedIcon /> },
  { label: "Ingressos", to: "/ingressos", icon: <ConfirmationNumberRoundedIcon /> },
];

const EVENTOS_SUBMENU: NavSubItem[] = [
  { label: "Lista de eventos", to: "/eventos", icon: <EventRoundedIcon /> },
  { label: "Novo evento", to: "/eventos/novo", icon: <EventRoundedIcon /> },
  { label: "Dados do evento", to: "/eventos/editar", icon: <EventRoundedIcon /> },
  { label: "Landing Page", to: "/eventos/formulario-lead", icon: <EventRoundedIcon /> },
  { label: "Gamificação", to: "/eventos/gamificacao", icon: <EventRoundedIcon /> },
  { label: "Ativações", to: "/eventos/ativacoes", icon: <EventRoundedIcon /> },
  { label: "Questionário", to: "/eventos/questionario", icon: <EventRoundedIcon /> },
];

export default function AppLayout() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const [filtersOpen, setFiltersOpen] = useState(false);
  const { user, logout } = useAuth();
  const { resolvedMode, toggleMode } = useThemeMode();
  const location = useLocation();
  const navigate = useNavigate();
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [navMenuAnchor, setNavMenuAnchor] = useState<null | HTMLElement>(null);
  const [submenuAnchor, setSubmenuAnchor] = useState<null | HTMLElement>(null);
  const [submenuKey, setSubmenuKey] = useState<string | null>(null);

  const navItems: NavItem[] = useMemo(
    () => [
      { label: "Dashboard", to: "/dashboard", icon: <DashboardRoundedIcon /> },
      {
        label: "Eventos",
        icon: <EventRoundedIcon />,
        children: EVENTOS_SUBMENU,
      },
      {
        label: "Ativos",
        icon: <ConfirmationNumberRoundedIcon />,
        children: ATIVOS_SUBMENU,
      },
      { label: "Leads", to: "/leads", icon: <PeopleAltRoundedIcon /> },
      { label: "Publicidade", to: "/publicidade", icon: <CampaignRoundedIcon /> },
      {
        label: "Patrocinados",
        to: "/patrocinados",
        icon: <VolunteerActivismRoundedIcon />,
      },
      { label: "Cupons", to: "/cupons", icon: <LocalOfferRoundedIcon /> },
    ],
    [],
  );

  const isPathActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(`${path}/`);

  const isNavItemActive = (item: NavItem) => {
    if (item.children) {
      return item.children.some((c) => isPathActive(c.to));
    }
    return item.to === "/dashboard" && location.pathname === "/success"
      ? true
      : item.to
        ? isPathActive(item.to)
        : false;
  };

  const handleSubItemClick = (to: string) => {
    navigate(to);
    setSubmenuAnchor(null);
    setSubmenuKey(null);
    setNavMenuAnchor(null);
  };

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Toolbar sx={{ px: 2 }}>
        <Typography variant="subtitle2" fontWeight={900} letterSpacing={0.2}>
          Filtros e funcionalidades
        </Typography>
      </Toolbar>
      <Divider />
      <Box sx={{ flex: 1, px: 2, py: 2, overflowY: "auto" }}>
        <Box id="app-sidebar-slot" />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          zIndex: (t) => t.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ gap: 1 }}>
          {!isDesktop && (
            <IconButton
              aria-label="Abrir filtros"
              edge="start"
              onClick={() => setFiltersOpen(true)}
              size="small"
            >
              <TuneRoundedIcon />
            </IconButton>
          )}
          {isDesktop ? (
            <Box
              component="nav"
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 0.5,
                flex: 1,
                minWidth: 0,
                overflowX: "auto",
                "&::-webkit-scrollbar": { height: 4 },
              }}
            >
              {navItems.map((item) => {
                const active = isNavItemActive(item);
                const key = item.to ?? item.label;
                if (item.children) {
                  const isThisMenuOpen = Boolean(submenuAnchor) && submenuKey === item.label;
                  return (
                    <Box key={key} component="span">
                      <Button
                        aria-haspopup="menu"
                        aria-expanded={isThisMenuOpen}
                        onClick={(e) => {
                          setSubmenuAnchor(e.currentTarget);
                          setSubmenuKey(item.label);
                        }}
                        startIcon={item.icon}
                        color={active ? "primary" : "inherit"}
                        size="small"
                        sx={{
                          fontWeight: active ? 800 : 600,
                          borderRadius: 2,
                          whiteSpace: "nowrap",
                          px: 1.5,
                          backgroundColor: active ? "action.selected" : "transparent",
                          "&:hover": {
                            backgroundColor: active ? "action.selected" : "action.hover",
                          },
                        }}
                      >
                        {item.label}
                      </Button>
                      <Menu
                        anchorEl={submenuAnchor}
                        open={isThisMenuOpen}
                        onClose={() => {
                          setSubmenuAnchor(null);
                          setSubmenuKey(null);
                        }}
                        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
                        transformOrigin={{ vertical: "top", horizontal: "left" }}
                      >
                        {item.children.map((sub) => (
                          <MenuItem
                            key={sub.to}
                            selected={isPathActive(sub.to)}
                            onClick={() => handleSubItemClick(sub.to)}
                          >
                            <ListItemIcon sx={{ minWidth: 36 }}>{sub.icon}</ListItemIcon>
                            <ListItemText primary={sub.label} />
                          </MenuItem>
                        ))}
                      </Menu>
                    </Box>
                  );
                }
                return (
                  <Button
                    key={key}
                    onClick={() => {
                      if (item.to) navigate(item.to);
                    }}
                    startIcon={item.icon}
                    color={active ? "primary" : "inherit"}
                    size="small"
                    sx={{
                      fontWeight: active ? 800 : 600,
                      borderRadius: 2,
                      whiteSpace: "nowrap",
                      px: 1.5,
                      backgroundColor: active ? "action.selected" : "transparent",
                      "&:hover": {
                        backgroundColor: active ? "action.selected" : "action.hover",
                      },
                    }}
                  >
                    {item.label}
                  </Button>
                );
              })}
            </Box>
          ) : (
            <>
              <IconButton
                aria-label="Abrir menu principal"
                onClick={(e) => setNavMenuAnchor(e.currentTarget)}
                size="small"
              >
                <MenuRoundedIcon />
              </IconButton>
              <Box sx={{ flex: 1 }} />
            </>
          )}
          <Button
            onClick={(e) => setUserMenuAnchor(e.currentTarget)}
            sx={{ fontWeight: 800, borderRadius: 2 }}
            color="inherit"
            startIcon={
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  bgcolor: "primary.main",
                  fontSize: 13,
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
                {user?.email || "Usuario"}
              </Typography>
              {user?.tipo_usuario ? (
                <Typography variant="caption" color="text.secondary" noWrap>
                  {String(user.tipo_usuario).toLowerCase()}
                </Typography>
              ) : null}
            </Box>
          </Button>
          <Menu
            anchorEl={navMenuAnchor}
            open={Boolean(navMenuAnchor)}
            onClose={() => {
              setNavMenuAnchor(null);
              setSubmenuAnchor(null);
              setSubmenuKey(null);
            }}
            anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
            transformOrigin={{ vertical: "top", horizontal: "left" }}
          >
            {navItems.map((item) => {
              const key = item.to ?? item.label;
              if (item.children) {
                const isThisSubmenuOpen = Boolean(submenuAnchor) && submenuKey === item.label;
                return (
                  <MenuItem
                    key={key}
                    aria-haspopup="menu"
                    aria-expanded={isThisSubmenuOpen}
                    selected={isNavItemActive(item)}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (isThisSubmenuOpen) {
                        setSubmenuAnchor(null);
                        setSubmenuKey(null);
                      } else {
                        setSubmenuAnchor(e.currentTarget);
                        setSubmenuKey(item.label);
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.label} />
                  </MenuItem>
                );
              }
              return (
                <MenuItem
                  key={key}
                  selected={isNavItemActive(item)}
                  onClick={() => {
                    setNavMenuAnchor(null);
                    if (item.to) navigate(item.to);
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </MenuItem>
              );
            })}
          </Menu>
          <Menu
            anchorEl={submenuAnchor}
            open={!isDesktop ? Boolean(submenuAnchor) : false}
            onClose={() => {
              setSubmenuAnchor(null);
              setSubmenuKey(null);
            }}
            anchorOrigin={{ vertical: "top", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "left" }}
          >
            {(navItems.find((i) => i.children && i.label === submenuKey)?.children ?? []).map(
              (sub) => (
                <MenuItem
                  key={sub.to}
                  selected={isPathActive(sub.to)}
                  onClick={() => handleSubItemClick(sub.to)}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>{sub.icon}</ListItemIcon>
                  <ListItemText primary={sub.label} />
                </MenuItem>
              ),
            )}
          </Menu>
          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={() => setUserMenuAnchor(null)}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem
              onClick={() => {
                toggleMode();
                setUserMenuAnchor(null);
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {resolvedMode === "dark" ? (
                  <LightModeRoundedIcon fontSize="small" />
                ) : (
                  <DarkModeRoundedIcon fontSize="small" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={resolvedMode === "dark" ? "Usar tema claro" : "Usar tema escuro"}
                secondary={resolvedMode === "dark" ? "Tema atual: escuro" : "Tema atual: claro"}
              />
            </MenuItem>
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
        open={isDesktop ? true : filtersOpen}
        onClose={() => setFiltersOpen(false)}
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
