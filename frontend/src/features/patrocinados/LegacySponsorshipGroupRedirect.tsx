import { Alert, Button, Stack } from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import { Link as RouterLink, Navigate, useParams } from "react-router-dom";

export default function LegacySponsorshipGroupRedirect() {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return <Alert severity="error">Identificador invalido.</Alert>;
  }

  if (/^\d+$/.test(id)) {
    return <Navigate to={`/patrocinados/grupos/${id}`} replace />;
  }

  return (
    <Stack spacing={2}>
      <Alert severity="warning">
        Compatibilidade limitada: a rota legada /patrocinados/:id agora so aceita IDs numericos
        de grupo. IDs locais antigos em formato texto/UUID nao possuem migracao automatica nem
        mapeamento para a rota nova.
      </Alert>
      <Button component={RouterLink} to="/patrocinados" startIcon={<ArrowBackRoundedIcon />}>
        Voltar para patrocinados
      </Button>
    </Stack>
  );
}
