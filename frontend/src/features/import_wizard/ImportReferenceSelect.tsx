import { FormControl, InputLabel, MenuItem, Select, Typography } from "@mui/material";

export type ImportReferenceOption = {
  value: string;
  label: string;
};

type ImportReferenceSelectProps = {
  enabled: boolean;
  value: string;
  options: ImportReferenceOption[];
  onChange: (nextValue: string) => void;
};

export default function ImportReferenceSelect({
  enabled,
  value,
  options,
  onChange,
}: ImportReferenceSelectProps) {
  if (!enabled) {
    return (
      <Typography variant="caption" color="text.secondary">
        -
      </Typography>
    );
  }

  return (
    <FormControl size="small" fullWidth>
      <InputLabel>Referencia</InputLabel>
      <Select
        label="Referencia"
        value={value}
        onChange={(event) => onChange(String(event.target.value || ""))}
      >
        <MenuItem value="">Selecionar</MenuItem>
        {options.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
