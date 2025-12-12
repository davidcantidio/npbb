import { useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { useAuth } from "../store/auth";

type Props = {
  children: React.ReactNode;
};

export function ProtectedRoute({ children }: Props) {
  const { token, user, loading, refresh } = useAuth();

  useEffect(() => {
    if (token && !user && !loading) {
      refresh();
    }
    if (!token && !loading) {
      window.location.href = "/login";
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
    return null;
  }

  return <>{children}</>;
}
