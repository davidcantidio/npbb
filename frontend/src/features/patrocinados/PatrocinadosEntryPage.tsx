import { Button, Paper, Stack, Typography } from "@mui/material";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import { Link as RouterLink } from "react-router-dom";

import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

export default function PatrocinadosEntryPage() {
  const apiMode = useSponsorshipApiMode();

  if (!apiMode) return <ApiRequiredPanel title="Novo cadastro em Patrocinados" />;

  return (
    <Stack spacing={2}>
      <Typography variant="h5" component="h1" fontWeight={800}>
        Novo cadastro em Patrocinados
      </Typography>
      <Typography color="text.secondary">
        Escolha a entidade de primeiro nivel. Contratos e contrapartidas continuam operando dentro
        de grupos.
      </Typography>

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack spacing={2}>
          <Button
            component={RouterLink}
            to="/patrocinados/pessoas/novo"
            variant="contained"
            endIcon={<ArrowForwardRoundedIcon />}
          >
            Nova pessoa
          </Button>
          <Button
            component={RouterLink}
            to="/patrocinados/instituicoes/novo"
            variant="contained"
            endIcon={<ArrowForwardRoundedIcon />}
          >
            Nova instituicao
          </Button>
          <Button
            component={RouterLink}
            to="/patrocinados/grupos/novo"
            variant="outlined"
            endIcon={<ArrowForwardRoundedIcon />}
          >
            Novo grupo
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
