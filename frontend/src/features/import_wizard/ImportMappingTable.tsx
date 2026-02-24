import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import ImportReferenceSelect, { type ImportReferenceOption } from "./ImportReferenceSelect";

export type ImportFieldOption = {
  value: string;
  label: string;
};

export type ImportMappingSuggestion = {
  campo: string | null;
  confianca: number | null;
};

export type ImportAliasDisplay = {
  canonical_value?: string | null;
  canonical_ref_id?: number | null;
};

type ImportMappingTableProps = {
  headers: string[];
  samplesByColumn: string[][];
  suggestions: ImportMappingSuggestion[];
  availableFields: ImportFieldOption[];
  aliasHits?: Array<ImportAliasDisplay | null>;
  referenceOptionsByField?: Record<string, ImportReferenceOption[]>;
  referenceSelections?: Record<number, string>;
  onChangeField: (index: number, nextField: string) => void;
  onChangeReference?: (index: number, nextValue: string) => void;
};

export default function ImportMappingTable({
  headers,
  samplesByColumn,
  suggestions,
  availableFields,
  aliasHits,
  referenceOptionsByField,
  referenceSelections,
  onChangeField,
  onChangeReference,
}: ImportMappingTableProps) {
  return (
    <Box>
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

      {headers.map((header, idx) => {
        const currentField = suggestions[idx]?.campo || "";
        const referenceOptions = (referenceOptionsByField?.[currentField] || []).map((option) => ({
          value: option.value,
          label: option.label,
        }));
        const referenceEnabled = Boolean(onChangeReference && referenceOptions.length > 0);
        return (
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
            }}
          >
            <Box>
              <Typography variant="body2" fontWeight={700}>
                {header || `Coluna ${idx + 1}`}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {samplesByColumn[idx]?.[0] || "-"}
              </Typography>
              {aliasHits?.[idx] ? (
                <Typography variant="caption" color="text.secondary" display="block">
                  Alias conhecido:{" "}
                  {aliasHits[idx]?.canonical_value ||
                    (aliasHits[idx]?.canonical_ref_id ? String(aliasHits[idx]?.canonical_ref_id) : "-")}
                </Typography>
              ) : null}
            </Box>

            <FormControl size="small" fullWidth>
              <InputLabel>Campo</InputLabel>
              <Select
                label="Campo"
                value={currentField}
                onChange={(event) => onChangeField(idx, String(event.target.value || ""))}
              >
                {availableFields.map((field) => (
                  <MenuItem key={field.value} value={field.value}>
                    {field.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <ImportReferenceSelect
              enabled={referenceEnabled}
              value={referenceSelections?.[idx] || ""}
              options={referenceOptions}
              onChange={(nextValue) => onChangeReference?.(idx, nextValue)}
            />

            <Box sx={{ textAlign: { xs: "left", md: "right" } }}>
              {suggestions[idx]?.confianca ? (
                <Typography variant="caption" color="text.secondary">
                  {Math.round((suggestions[idx].confianca || 0) * 100)}%
                </Typography>
              ) : (
                <Typography variant="caption" color="text.secondary">
                  -
                </Typography>
              )}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
