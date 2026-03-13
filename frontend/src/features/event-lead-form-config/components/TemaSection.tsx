import { Autocomplete, Box, TextField, Typography } from "@mui/material";
import type { FormularioTemplate } from "../../../services/eventos";

type TemaSectionProps = {
  templates: FormularioTemplate[];
  templateId: number | null;
  onTemplateChange: (templateId: number | null) => void;
};

export function TemaSection({
  templates,
  templateId,
  onTemplateChange,
}: TemaSectionProps) {
  const selectedTemplate =
    templateId == null
      ? null
      : templates.find((t) => t.id === templateId) ?? null;

  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={900} gutterBottom>
        Tema
      </Typography>
      <Autocomplete
        options={templates}
        value={selectedTemplate}
        onChange={(_, value) => onTemplateChange(value ? value.id : null)}
        getOptionLabel={(option) => option.nome}
        isOptionEqualToValue={(option, value) => option.id === value.id}
        sx={{ width: "100%" }}
        renderInput={(params) => (
          <TextField {...params} label="Tema" placeholder="Selecione..." />
        )}
      />
      <Typography variant="caption" color="text.secondary" display="block" sx={{ pt: 0.5 }}>
        O preview atualiza em tempo real; clique em &quot;Salvar&quot; apenas para persistir.
      </Typography>
    </Box>
  );
}
