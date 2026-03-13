import { Box, Checkbox, FormControlLabel, Stack, Typography } from "@mui/material";

type CamposSectionProps = {
  camposPossiveisUniq: string[];
  camposAtivos: Set<string>;
  camposObrigatorios: Record<string, boolean>;
  onToggleCampo: (nome: string) => void;
  onSetObrigatorio: (nome: string, obrigatorio: boolean) => void;
};

export function CamposSection({
  camposPossiveisUniq,
  camposAtivos,
  camposObrigatorios,
  onToggleCampo,
  onSetObrigatorio,
}: CamposSectionProps) {
  return (
    <>
      <Box>
        <Typography variant="subtitle1" fontWeight={900} gutterBottom>
          Campos possíveis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Marque os campos que estarão ativos no formulário. O preview responde imediatamente;
          &quot;Salvar&quot; persiste a configuração.
        </Typography>
      </Box>

      {camposPossiveisUniq.length ? (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
            columnGap: 3,
            rowGap: 1,
          }}
        >
          {camposPossiveisUniq.map((nome, index) => {
            const ativo = camposAtivos.has(nome);
            const obrigatorio = ativo ? (camposObrigatorios[nome] ?? true) : false;

            return (
              <Box
                key={nome}
                data-testid={`lead-field-card-${nome.toLowerCase().replace(/\s+/g, "-")}`}
                sx={{
                  px: 1.5,
                  py: 0.75,
                  borderRadius: 2,
                  border: 1,
                  borderColor: "divider",
                  backgroundColor: ativo ? "rgba(103, 80, 164, 0.05)" : "transparent",
                }}
              >
                <Stack
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                  gap={1}
                  flexWrap="wrap"
                >
                  <Box>
                    <Typography variant="body2" fontWeight={800} lineHeight={1.2}>
                      {nome}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ordem {index}
                    </Typography>
                  </Box>

                  <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                    <FormControlLabel
                      sx={{ m: 0 }}
                      control={
                        <Checkbox
                          size="small"
                          checked={ativo}
                          onChange={() => onToggleCampo(nome)}
                        />
                      }
                      label="Ativo"
                    />
                    <FormControlLabel
                      sx={{ m: 0 }}
                      control={
                        <Checkbox
                          size="small"
                          checked={obrigatorio}
                          disabled={!ativo}
                          onChange={(_, checked) => onSetObrigatorio(nome, checked)}
                        />
                      }
                      label="Obrigatório"
                    />
                  </Stack>
                </Stack>
              </Box>
            );
          })}
        </Box>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum campo disponível.
        </Typography>
      )}
    </>
  );
}
