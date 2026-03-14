import { useState } from "react";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import { Box, Button, Checkbox, Collapse, FormControlLabel, Stack, Typography } from "@mui/material";

type CamposSectionProps = {
  camposAtivosOrdenados: string[];
  camposDisponiveis: string[];
  camposAtivos: Set<string>;
  camposObrigatorios: Record<string, boolean>;
  isCampoSempreObrigatorio: (nome: string) => boolean;
  onToggleCampo: (nome: string) => void;
  onSetObrigatorio: (nome: string, obrigatorio: boolean) => void;
};

export function CamposSection({
  camposAtivosOrdenados,
  camposDisponiveis,
  camposAtivos,
  camposObrigatorios,
  isCampoSempreObrigatorio,
  onToggleCampo,
  onSetObrigatorio,
}: CamposSectionProps) {
  const [showCamposDisponiveis, setShowCamposDisponiveis] = useState(false);

  return (
    <>
      <Box>
        <Typography variant="subtitle1" fontWeight={900} gutterBottom>
          Campos possíveis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Os campos ativos aparecem em uma lista única. Use o botão &quot;+&quot; para revelar
          opções adicionais; o preview responde imediatamente e &quot;Salvar&quot; persiste a
          configuração.
        </Typography>
      </Box>

      {camposAtivosOrdenados.length || camposDisponiveis.length ? (
        <Stack spacing={1.25}>
          {camposAtivosOrdenados.map((nome) => {
            const ativo = camposAtivos.has(nome);
            const obrigatorio = ativo ? (camposObrigatorios[nome] ?? true) : false;
            const campoTravado = isCampoSempreObrigatorio(nome);

            return (
              <Box
                key={nome}
                data-testid={`lead-field-card-${nome.toLowerCase().replace(/\s+/g, "-")}`}
                sx={{
                  px: 1.5,
                  py: 1,
                  borderRadius: 2,
                  border: 1,
                  borderColor: "divider",
                  backgroundColor: ativo ? "rgba(103, 80, 164, 0.05)" : "transparent",
                }}
              >
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  alignItems={{ xs: "flex-start", sm: "center" }}
                  justifyContent="space-between"
                  gap={1.5}
                >
                  <Box>
                    <Typography variant="body2" fontWeight={800} lineHeight={1.2}>
                      {nome}
                    </Typography>
                    {campoTravado ? (
                      <Typography variant="caption" color="text.secondary">
                        Campo obrigatório por padrão.
                      </Typography>
                    ) : null}
                  </Box>

                  <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                    <FormControlLabel
                      sx={{ m: 0 }}
                      control={
                        <Checkbox
                          size="small"
                          checked={ativo}
                          disabled={campoTravado}
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
                          disabled={!ativo || campoTravado}
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

          {camposDisponiveis.length ? (
            <>
              <Button
                variant="outlined"
                color="inherit"
                startIcon={<AddRoundedIcon />}
                onClick={() => setShowCamposDisponiveis((prev) => !prev)}
                sx={{ alignSelf: "flex-start", borderRadius: 999 }}
              >
                {showCamposDisponiveis ? "Ocultar campos" : "Adicionar campo"}
              </Button>

              <Collapse in={showCamposDisponiveis}>
                <Stack spacing={1.25} sx={{ pt: 0.5 }}>
                  {camposDisponiveis.map((nome) => (
                    <Box
                      key={nome}
                      data-testid={`lead-field-option-${nome.toLowerCase().replace(/\s+/g, "-")}`}
                      sx={{
                        px: 1.5,
                        py: 1,
                        borderRadius: 2,
                        border: 1,
                        borderStyle: "dashed",
                        borderColor: "divider",
                        backgroundColor: "background.default",
                      }}
                    >
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        alignItems={{ xs: "flex-start", sm: "center" }}
                        justifyContent="space-between"
                        gap={1.5}
                      >
                        <Typography variant="body2" fontWeight={700}>
                          {nome}
                        </Typography>

                        <FormControlLabel
                          sx={{ m: 0 }}
                          control={
                            <Checkbox
                              size="small"
                              checked={false}
                              onChange={() => onToggleCampo(nome)}
                            />
                          }
                          label="Ativo"
                        />
                      </Stack>
                    </Box>
                  ))}
                </Stack>
              </Collapse>
            </>
          ) : null}
        </Stack>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum campo disponível.
        </Typography>
      )}
    </>
  );
}
