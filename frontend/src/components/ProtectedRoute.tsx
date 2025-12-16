import { useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../store/auth";

type Props = {
  children: React.ReactNode;
};

export function ProtectedRoute({ children }: Props) {
  const { token, user, loading, refresh } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (token && !user && !loading) {
      refresh();
    }
  }, [token, user, loading, refresh]);

  if (loading || (token && !user)) {
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

  return <>{children}</>;
}
