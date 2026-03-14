import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  MenuItem,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import type { CreateForm } from "../hooks";
import { MAX_LEN } from "../hooks";
import type { EventoRead } from "../../../services/eventos";
import type { Gamificacao } from "../../../services/eventos";

type SetCreateFormField = <K extends keyof CreateForm>(key: K, value: CreateForm[K]) => void;

export type AtivacaoFormSectionProps = {
  form: CreateForm;
  onFormChange: SetCreateFormField;
  gamificacoes: Gamificacao[];
  disabled: boolean;
  isEditing: boolean;
  editing: { nome: string } | null;
  evento: EventoRead | null;
  eventoId: number;
  createError: string | null;
  nomeRequiredError: boolean;
  onSubmit: () => void;
  onReset: () => void;
  isBusy: boolean;
  creating: boolean;
  saving: boolean;
};

export function AtivacaoFormSection({
  form,
  onFormChange,
  gamificacoes,
  disabled,
  isEditing,
  editing,
  evento,
  eventoId,
  createError,
  nomeRequiredError,
  onSubmit,
  onReset,
  isBusy: _isBusy,
  creating,
  saving,
}: AtivacaoFormSectionProps) {
  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="subtitle1" fontWeight={900} gutterBottom>
          {isEditing ? "Editar ativacao" : "Nova ativacao"}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {isEditing
            ? `Atualize a ativacao "${editing?.nome || ""}" sem sair do evento.`
            : evento?.nome
              ? `Evento: ${evento.nome}`
              : `Evento #${eventoId}`}
        </Typography>
      </Box>

      {createError && <Alert severity="error">{createError}</Alert>}

      <Stack spacing={2}>
        <TextField
          label="Nome da ativação"
          value={form.nome}
          onChange={(e) => onFormChange("nome", e.target.value)}
          disabled={disabled}
          required
          error={Boolean(nomeRequiredError)}
          helperText={
            nomeRequiredError ? "Nome obrigatorio." : `${form.nome.length}/${MAX_LEN.nome}`
          }
          fullWidth
          inputProps={{ maxLength: MAX_LEN.nome }}
        />

        <TextField
          label="Mensagem do QR Code"
          value={form.mensagem_qrcode}
          onChange={(e) => onFormChange("mensagem_qrcode", e.target.value)}
          disabled={disabled}
          multiline
          minRows={2}
          helperText={`${form.mensagem_qrcode.length}/${MAX_LEN.mensagem_qrcode} caracteres`}
          fullWidth
          inputProps={{ maxLength: MAX_LEN.mensagem_qrcode }}
        />

        <TextField
          label="Descricao"
          value={form.descricao}
          onChange={(e) => onFormChange("descricao", e.target.value)}
          disabled={disabled}
          multiline
          minRows={2}
          helperText={`${form.descricao.length}/${MAX_LEN.descricao} caracteres`}
          fullWidth
          inputProps={{ maxLength: MAX_LEN.descricao }}
        />

        <TextField
          select
          label="Tipo de gamificação"
          value={form.gamificacao_id ?? ""}
          onChange={(e) => {
            const raw = e.target.value;
            const parsed = raw === "" ? null : Number(raw);
            onFormChange("gamificacao_id", parsed != null && Number.isFinite(parsed) ? parsed : null);
          }}
          disabled={disabled}
          fullWidth
        >
          <MenuItem value="">Nenhuma</MenuItem>
          {gamificacoes.map((g) => (
            <MenuItem key={g.id} value={g.id}>
              {g.nome}
            </MenuItem>
          ))}
        </TextField>

        <Stack direction="row" flexWrap="wrap" columnGap={3} rowGap={1}>
          <FormControlLabel
            control={
              <Switch
                checked={form.redireciona_pesquisa}
                disabled={disabled}
                onChange={(_, checked) => onFormChange("redireciona_pesquisa", checked)}
              />
            }
            label="Redirecionamento para tela de pesquisa"
          />
          <FormControlLabel
            control={
              <Switch
                checked={form.checkin_unico}
                disabled={disabled}
                onChange={(_, checked) => onFormChange("checkin_unico", checked)}
              />
            }
            label="Conversao unica por CPF"
          />
          <FormControlLabel
            control={
              <Switch
                checked={form.termo_uso}
                disabled={disabled}
                onChange={(_, checked) => onFormChange("termo_uso", checked)}
              />
            }
            label="Termo de uso"
          />
          <FormControlLabel
            control={
              <Switch
                checked={form.gera_cupom}
                disabled={disabled}
                onChange={(_, checked) => onFormChange("gera_cupom", checked)}
              />
            }
            label="Gerar Cupom"
          />
        </Stack>

        <Stack direction={{ xs: "column", sm: "row" }} justifyContent="flex-end" spacing={1}>
          {isEditing ? (
            <Button
              variant="outlined"
              onClick={onReset}
              disabled={disabled}
              size="small"
              sx={{ textTransform: "none", whiteSpace: "nowrap" }}
            >
              Cancelar edicao
            </Button>
          ) : null}
          <Button
            variant="contained"
            onClick={onSubmit}
            disabled={disabled}
            size="small"
            sx={{ textTransform: "none", whiteSpace: "nowrap", fontWeight: 800 }}
          >
            {creating || saving ? (
              <CircularProgress size={22} color="inherit" />
            ) : isEditing ? (
              "Salvar ativacao"
            ) : (
              "Adicionar ativacao"
            )}
          </Button>
        </Stack>
      </Stack>
    </Stack>
  );
}
