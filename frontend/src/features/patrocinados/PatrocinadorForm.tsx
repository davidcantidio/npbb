import {
  FormControlLabel,
  Stack,
  Switch,
  TextField,
} from "@mui/material";

import type { PatrocinadorInput } from "../../types/patrocinados";

type PatrocinadorFormProps = {
  value: PatrocinadorInput;
  onChange: (next: PatrocinadorInput) => void;
  disabled?: boolean;
};

export function PatrocinadorForm({ value, onChange, disabled }: PatrocinadorFormProps) {
  const patch = (partial: Partial<PatrocinadorInput>) => {
    onChange({ ...value, ...partial });
  };

  return (
    <Stack spacing={2}>
      <TextField
        label="Nome fantasia"
        value={value.nome_fantasia}
        onChange={(e) => patch({ nome_fantasia: e.target.value })}
        disabled={disabled}
        required
        fullWidth
      />
      <TextField
        label="Razão social"
        value={value.razao_social}
        onChange={(e) => patch({ razao_social: e.target.value })}
        disabled={disabled}
        fullWidth
      />
      <TextField
        label="CNPJ"
        value={value.cnpj}
        onChange={(e) => patch({ cnpj: e.target.value })}
        disabled={disabled}
        fullWidth
      />
      <TextField
        label="E-mail"
        type="email"
        value={value.email}
        onChange={(e) => patch({ email: e.target.value })}
        disabled={disabled}
        fullWidth
      />
      <TextField
        label="Telefone"
        value={value.telefone}
        onChange={(e) => patch({ telefone: e.target.value })}
        disabled={disabled}
        fullWidth
      />
      <TextField
        label="Site"
        value={value.site}
        onChange={(e) => patch({ site: e.target.value })}
        disabled={disabled}
        fullWidth
      />
      <TextField
        label="Observações"
        value={value.observacoes}
        onChange={(e) => patch({ observacoes: e.target.value })}
        disabled={disabled}
        multiline
        minRows={3}
        fullWidth
      />
      <FormControlLabel
        control={
          <Switch
            checked={value.ativo}
            onChange={(e) => patch({ ativo: e.target.checked })}
            disabled={disabled}
          />
        }
        label="Ativo"
      />
    </Stack>
  );
}
