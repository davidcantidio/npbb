import { Button } from "@mui/material";

type LeadImportUploadProps = {
  label?: string;
  accept?: string;
  disabled?: boolean;
  onSelectFile: (file: File) => void;
};

/**
 * Upload trigger used by the leads import flow.
 */
export function LeadImportUpload({ label = "Importar CSV/XLSX", accept = ".csv,.xlsx", disabled, onSelectFile }: LeadImportUploadProps) {
  return (
    <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700 }} component="label" disabled={disabled}>
      {label}
      <input
        type="file"
        hidden
        accept={accept}
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
