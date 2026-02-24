import { useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../store/auth";

type Props = {
  children: React.ReactNode;
};

/**
 * Guards authenticated routes and triggers a session refresh when needed.
 * @param params.children Route element tree that requires authentication.
 * @returns Protected content when session is valid, otherwise redirect/loading states.
 */
export function ProtectedRoute({ children }: Props) {
  const { token, user, loading, refreshing, refresh } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (token && !user && !loading && !refreshing) {
      refresh();
    }
  }, [token, user, loading, refreshing, refresh]);

  if (loading || refreshing) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: 1,
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Verificando sessao...
        </Typography>
      </Box>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
