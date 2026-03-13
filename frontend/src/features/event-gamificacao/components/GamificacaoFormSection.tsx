import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import type { CreateForm } from "../hooks";
import { MAX_LEN } from "../hooks";
import type { Gamificacao } from "../../../services/eventos";

function normalizeText(value: string) {
  return String(value || "").trim();
}

type SetCreateFormField = <K extends keyof CreateForm>(key: K, value: CreateForm[K]) => void;

export type GamificacaoFormSectionProps = {
  form: CreateForm;
  onFormChange: SetCreateFormField;
  disabled: boolean;
  isEditing: boolean;
  editing: Gamificacao | null;
  createError: string | null;
  createAttempted: boolean;
  onSubmit: () => void;
  onCancelEdit: () => void;
  isBusy: boolean;
  creating: boolean;
  saving: boolean;
};

export function GamificacaoFormSection({
  form,
  onFormChange,
  disabled,
  isEditing,
  editing,
  createError,
  createAttempted,
  onSubmit,
  onCancelEdit,
  isBusy,
  creating,
  saving,
}: GamificacaoFormSectionProps) {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        borderRadius: 3,
        width: "100%",
        maxWidth: { xs: "100%", md: 420 },
        flexShrink: 0,
      }}
    >
      <Typography variant="h6" fontWeight={900} gutterBottom>
        {isEditing ? "Editar gamificação" : "Adicionar gamificação"}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {isEditing
          ? `Editando a gamificação "${editing?.nome || ""}" (#${editing?.id ?? ""}).`
          : "Cadastre gamificações do evento. Na etapa de Ativações você poderá selecionar uma delas (ou Nenhuma)."}
      </Typography>

      {createError && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {createError}
        </Alert>
      )}

      <Stack spacing={2}>
        <TextField
          label="Nome da gamificação"
          required
          value={form.nome}
          inputProps={{ maxLength: MAX_LEN.nome }}
          onChange={(e) => onFormChange("nome", e.target.value)}
          disabled={disabled}
          fullWidth
          error={createAttempted && !normalizeText(form.nome)}
          helperText={createAttempted && !normalizeText(form.nome) ? "Informe o nome da gamificação." : "\u00A0"}
        />
        <TextField
          label="Descrição"
          required
          value={form.descricao}
          inputProps={{ maxLength: MAX_LEN.descricao }}
          onChange={(e) => onFormChange("descricao", e.target.value)}
          disabled={disabled}
          multiline
          minRows={4}
          fullWidth
          error={createAttempted && !normalizeText(form.descricao)}
          helperText={
            <Box component="span" sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
              <Box component="span">
                {createAttempted && !normalizeText(form.descricao) ? "Informe a descrição." : "\u00A0"}
              </Box>
              <Box component="span">{`${form.descricao.length}/${MAX_LEN.descricao} caracteres`}</Box>
            </Box>
          }
        />
        <TextField
          label="Prêmio"
          required
          value={form.premio}
          inputProps={{ maxLength: MAX_LEN.premio }}
          onChange={(e) => onFormChange("premio", e.target.value)}
          disabled={disabled}
          fullWidth
          error={createAttempted && !normalizeText(form.premio)}
          helperText={createAttempted && !normalizeText(form.premio) ? "Informe o prêmio." : "\u00A0"}
        />
        <TextField
          label="Título do feedback de sucesso"
          required
          value={form.titulo_feedback}
          inputProps={{ maxLength: MAX_LEN.titulo_feedback }}
          onChange={(e) => onFormChange("titulo_feedback", e.target.value)}
          disabled={disabled}
          fullWidth
          error={createAttempted && !normalizeText(form.titulo_feedback)}
          helperText={
            createAttempted && !normalizeText(form.titulo_feedback)
              ? "Informe o título do feedback."
              : "\u00A0"
          }
        />
        <TextField
          label="Descrição do feedback de sucesso"
          required
          value={form.texto_feedback}
          inputProps={{ maxLength: MAX_LEN.texto_feedback }}
          onChange={(e) => onFormChange("texto_feedback", e.target.value)}
          disabled={disabled}
          multiline
          minRows={4}
          fullWidth
          error={createAttempted && !normalizeText(form.texto_feedback)}
          helperText={
            <Box component="span" sx={{ display: "flex", justifyContent: "space-between", gap: 1 }}>
              <Box component="span">
                {createAttempted && !normalizeText(form.texto_feedback)
                  ? "Informe a descrição do feedback."
                  : "\u00A0"}
              </Box>
              <Box component="span">{`${form.texto_feedback.length}/${MAX_LEN.texto_feedback} caracteres`}</Box>
            </Box>
          }
        />

        <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems="stretch">
          {isEditing && (
            <Button
              variant="outlined"
              disabled={disabled || isBusy}
              onClick={onCancelEdit}
              sx={{ textTransform: "none" }}
            >
              Cancelar
            </Button>
          )}
          <Button
            variant="contained"
            disabled={disabled || isBusy}
            onClick={onSubmit}
            sx={{ fontWeight: 800, textTransform: "none" }}
          >
            {saving || creating ? (
              <CircularProgress size={22} color="inherit" />
            ) : isEditing ? (
              "Atualizar gamificação"
            ) : (
              "Adicionar gamificação"
            )}
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
}
