import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import { LeadImportPreview } from "../../../services/leads_import";

export type LeadMappingFieldOption = {
  value: string;
  label: string;
};

type LeadMappingTableProps = {
  preview: LeadImportPreview;
  availableFields: LeadMappingFieldOption[];
  secondarySelections: Record<number, string>;
  activeRowIndex: number | null;
  referenceOptions: Record<string, Array<{ value: string; label: string }>>;
  mappingError: string | null;
  aliasWarning: string | null;
  importError: string | null;
  loading: boolean;
  onFieldChange: (index: number, campo: string | null) => void;
  onSecondaryChange: (index: number, value: string) => void;
  onFocusRow: (index: number | null) => void;
  onImport: () => void;
};

/**
 * Renders mapping matrix and import CTA for lead assisted import.
 */
export function LeadMappingTable({
  preview,
  availableFields,
  secondarySelections,
  activeRowIndex,
  referenceOptions,
  mappingError,
  aliasWarning,
  importError,
  loading,
  onFieldChange,
  onSecondaryChange,
  onFocusRow,
  onImport,
}: LeadMappingTableProps) {
  return (
    <Box>
      <Typography variant="subtitle1" fontWeight={800} gutterBottom>
        Mapeamento de colunas
      </Typography>
      <Typography variant="caption" color="text.secondary" gutterBottom sx={{ display: "block", mb: 2 }}>
        Obrigatorio: Email ou CPF.
      </Typography>

      <Box
        sx={{
          display: { xs: "none", md: "grid" },
          gridTemplateColumns: "1.6fr 1fr 1fr 0.6fr",
          gap: 2,
          mb: 1,
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Coluna / amostra
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Campo
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Referencia
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ textAlign: "right" }}>
          Confianca
        </Typography>
      </Box>

      {preview.headers.map((header, idx) => (
        <Box
          key={`${header}-${idx}`}
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "1.6fr 1fr 1fr 0.6fr" },
            gap: 2,
            alignItems: "center",
            mb: 1.5,
            pb: 1.5,
            borderBottom: "1px solid rgba(0,0,0,0.06)",
            borderRadius: 2,
            px: { xs: 0, md: 1 },
            backgroundColor: activeRowIndex === idx ? "rgba(92, 71, 163, 0.08)" : "transparent",
            transition: "background-color 150ms ease",
          }}
        >
          <Box>
            <Typography variant="body2" fontWeight={700}>
              {header || `Coluna ${idx + 1}`}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {preview.samples_by_column[idx]?.[0] || "-"}
            </Typography>
            {preview.alias_hits?.[idx] ? (
              <Typography variant="caption" color="text.secondary">
                Alias conhecido: {preview.alias_hits[idx]?.canonical_value || preview.alias_hits[idx]?.evento_id || "-"}
              </Typography>
            ) : null}
          </Box>

          <FormControl
            size="small"
            fullWidth
            sx={{
              "& .MuiOutlinedInput-root": { borderRadius: 2 },
              "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
                borderColor: "#5C47A3",
                borderWidth: 2,
                boxShadow: "0 0 0 2px rgba(92,71,163,0.15)",
              },
            }}
          >
            <InputLabel>Campo</InputLabel>
            <Select
              label="Campo"
              value={preview.suggestions[idx]?.campo || ""}
              onChange={(event) => onFieldChange(idx, String(event.target.value || "") || null)}
              onFocus={() => onFocusRow(idx)}
              onBlur={() => onFocusRow(null)}
            >
              {availableFields.map((field) => (
                <MenuItem key={field.value} value={field.value}>
                  {field.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box>
            {["evento_nome", "cidade", "estado", "genero"].includes(preview.suggestions[idx]?.campo || "") ? (
              <FormControl size="small" fullWidth>
                <InputLabel>Referencia</InputLabel>
                <Select
                  label="Referencia"
                  value={secondarySelections[idx] || ""}
                  onChange={(event) => onSecondaryChange(idx, String(event.target.value || ""))}
                  onFocus={() => onFocusRow(idx)}
                  onBlur={() => onFocusRow(null)}
                >
                  <MenuItem value="">Selecionar</MenuItem>
                  {(referenceOptions[preview.suggestions[idx]?.campo || ""] || []).map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Typography variant="caption" color="text.secondary">
                -
              </Typography>
            )}
          </Box>

          <Box sx={{ textAlign: { xs: "left", md: "right" } }}>
            {preview.suggestions[idx]?.confianca ? (
              <Typography variant="caption" color="text.secondary">
                {Math.round((preview.suggestions[idx].confianca || 0) * 100)}%
              </Typography>
            ) : (
              <Typography variant="caption" color="text.secondary">
                -
              </Typography>
            )}
          </Box>
        </Box>
      ))}

      {mappingError ? <Alert severity="error" sx={{ mb: 2 }}>{mappingError}</Alert> : null}
      {aliasWarning ? <Alert severity="warning" sx={{ mb: 2 }}>{aliasWarning}</Alert> : null}

      <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700, ml: 1 }} onClick={onImport} disabled={loading}>
        Importar
      </Button>

      {importError ? <Alert severity="error" sx={{ mt: 2 }}>{importError}</Alert> : null}
    </Box>
  );
}
