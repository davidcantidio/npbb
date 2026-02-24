import { Button } from "@mui/material";

type LeadImportUploadProps = {
  disabled?: boolean;
  onSelectFile: (file: File) => void;
};

/**
 * Upload trigger used by the leads import flow.
 */
export function LeadImportUpload({ disabled, onSelectFile }: LeadImportUploadProps) {
  return (
    <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700 }} component="label" disabled={disabled}>
      Importar CSV/XLSX
      <input
        type="file"
        hidden
        accept=".csv,.xlsx"
        onChange={(event) => {
          const selected = event.target.files?.[0];
          if (!selected) return;
          onSelectFile(selected);
          event.currentTarget.value = "";
        }}
      />
    </Button>
  );
}
