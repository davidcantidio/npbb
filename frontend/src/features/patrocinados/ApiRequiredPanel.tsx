import { Alert, Button, Stack, Typography } from "@mui/material";
import SettingsEthernetRoundedIcon from "@mui/icons-material/SettingsEthernetRounded";

type ApiRequiredPanelProps = {
  title?: string;
};

export default function ApiRequiredPanel({
  title = "Patrocinados dependem da API",
}: ApiRequiredPanelProps) {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" component="h1" fontWeight={800}>
        {title}
      </Typography>
      <Alert severity="warning">
        Este modulo nao usa mais o fallback local. Defina <code>VITE_SPONSORSHIP_USE_API=true</code>{" "}
        e aponte o frontend para o backend antes de usar Patrocinados.
      </Alert>
      <Button
        variant="outlined"
        color="inherit"
        startIcon={<SettingsEthernetRoundedIcon />}
        disabled
      >
        API obrigatoria
      </Button>
    </Stack>
  );
}
