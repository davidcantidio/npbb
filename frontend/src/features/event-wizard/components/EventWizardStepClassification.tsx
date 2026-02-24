import { Autocomplete, Box, Chip, CircularProgress, Stack, TextField, Typography } from "@mui/material";
import {
  DivisaoDemandante,
  Diretoria,
  SubtipoEvento,
  Tag,
  Territorio,
  TipoEvento,
} from "../../../services/eventos";
import { EventWizardFormErrors, EventWizardFormState } from "../hooks/useEventWizardForm";

type EventWizardStepClassificationProps = {
  visible: boolean;
  form: EventWizardFormState;
  errors: EventWizardFormErrors;
  diretorias: Diretoria[];
  divisoesDemandantes: DivisaoDemandante[];
  tipos: TipoEvento[];
  subtipos: SubtipoEvento[];
  tags: Tag[];
  territorios: Territorio[];
  selectedDiretoria: Diretoria | null;
  selectedDivisaoDemandante: DivisaoDemandante | null;
  selectedTipo: TipoEvento | null;
  selectedSubtipo: SubtipoEvento | null;
  selectedTerritorios: Territorio[];
  selectedTagValues: Array<Tag | string>;
  selectedTipoId: number | null;
  loadingDomains: boolean;
  loadingSubtipos: boolean;
  setFieldRef: (fieldId: string) => (node: HTMLDivElement | null) => void;
  getFieldSx: (fieldId: string, base?: unknown) => unknown;
  getFieldHelperText: (field: keyof EventWizardFormState, base?: string) => string | undefined;
  preventEnterSubmitOnClassification: (event: React.KeyboardEvent<HTMLElement>) => void;
  onDiretoriaChange: (diretoriaId: string) => void;
  onDivisaoDemandanteChange: (divisaoId: string) => void;
  onTipoChange: (_: unknown, value: TipoEvento | null) => void;
  onSubtipoChange: (subtipoId: string) => void;
  onTerritoriosChange: (territorioIds: string[]) => void;
  onTagsChange: (values: Array<Tag | string>) => void;
};

/**
 * Renders event classification controls (hierarchies, tags and territories).
 */
export function EventWizardStepClassification({
  visible,
  form,
  errors,
  diretorias,
  divisoesDemandantes,
  tipos,
  subtipos,
  tags,
  territorios,
  selectedDiretoria,
  selectedDivisaoDemandante,
  selectedTipo,
  selectedSubtipo,
  selectedTerritorios,
  selectedTagValues,
  selectedTipoId,
  loadingDomains,
  loadingSubtipos,
  setFieldRef,
  getFieldSx,
  getFieldHelperText,
  preventEnterSubmitOnClassification,
  onDiretoriaChange,
  onDivisaoDemandanteChange,
  onTipoChange,
  onSubtipoChange,
  onTerritoriosChange,
  onTagsChange,
}: EventWizardStepClassificationProps) {
  if (!visible) return null;

  return (
    <Box>
      <Typography variant="h6" fontWeight={800}>
        Classificacao
      </Typography>

      <Stack spacing={2} sx={{ pt: 1 }}>
        <Box ref={setFieldRef("diretoria_id")} sx={getFieldSx("diretoria_id") as object}>
          <Autocomplete
            options={diretorias}
            value={selectedDiretoria}
            onKeyDown={preventEnterSubmitOnClassification}
            onChange={(_, value) => onDiretoriaChange(value ? String(value.id) : "")}
            getOptionLabel={(option) => option.nome}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            disabled={loadingDomains}
            fullWidth
            renderInput={(params) => (
              <TextField
                {...params}
                label="Diretoria"
                fullWidth
                helperText={getFieldHelperText("diretoria_id", "Opcional")}
              />
            )}
          />
        </Box>

        <Box ref={setFieldRef("divisao_demandante_id")} sx={getFieldSx("divisao_demandante_id") as object}>
          <Autocomplete
            options={divisoesDemandantes}
            value={selectedDivisaoDemandante}
            onKeyDown={preventEnterSubmitOnClassification}
            onChange={(_, value) => onDivisaoDemandanteChange(value ? String(value.id) : "")}
            getOptionLabel={(option) => option.nome}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            disabled={loadingDomains}
            fullWidth
            renderInput={(params) => (
              <TextField
                {...params}
                label="Divisao demandante"
                placeholder="Selecione uma Divisao demandante"
                fullWidth
                error={Boolean(errors.divisao_demandante_id)}
                helperText={getFieldHelperText("divisao_demandante_id")}
              />
            )}
          />
        </Box>

        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Box ref={setFieldRef("tipo_id")} sx={getFieldSx("tipo_id", { flex: 1 }) as object}>
            <Autocomplete
              options={tipos}
              value={selectedTipo}
              onKeyDown={preventEnterSubmitOnClassification}
              onChange={onTipoChange}
              getOptionLabel={(option) => option.nome}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              disabled={loadingDomains}
              sx={{ flex: 1 }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Tipo de evento"
                  placeholder="Selecione um Tipo de Evento"
                  fullWidth
                  helperText={getFieldHelperText("tipo_id", "Opcional")}
                />
              )}
            />
          </Box>

          <Box ref={setFieldRef("subtipo_id")} sx={getFieldSx("subtipo_id", { flex: 1 }) as object}>
            <Autocomplete
              options={subtipos}
              value={selectedSubtipo}
              onKeyDown={preventEnterSubmitOnClassification}
              onChange={(_, value) => onSubtipoChange(value ? String(value.id) : "")}
              getOptionLabel={(option) => option.nome}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              disabled={!selectedTipoId || loadingSubtipos || loadingDomains}
              loading={loadingSubtipos}
              sx={{ flex: 1 }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Subtipo"
                  placeholder="Selecione um Subtipo"
                  fullWidth
                  error={Boolean(errors.subtipo_id)}
                  helperText={getFieldHelperText("subtipo_id")}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loadingSubtipos ? <CircularProgress color="inherit" size={18} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Box>
        </Stack>

        <Box ref={setFieldRef("territorio_ids")} sx={getFieldSx("territorio_ids") as object}>
          <Autocomplete
            multiple
            options={territorios}
            value={selectedTerritorios}
            onKeyDown={preventEnterSubmitOnClassification}
            onChange={(_, values) => onTerritoriosChange(values.map((value) => String(value.id)))}
            disableCloseOnSelect
            getOptionLabel={(option) => option.nome}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            disabled={loadingDomains}
            fullWidth
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip {...getTagProps({ index })} key={option.id} label={option.nome} size="small" />
              ))
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Territorios"
                placeholder={selectedTerritorios.length ? "" : "Selecione os territorios"}
                fullWidth
                helperText={getFieldHelperText("territorio_ids")}
              />
            )}
          />
        </Box>

        <Box ref={setFieldRef("tag_ids")} sx={getFieldSx("tag_ids") as object}>
          <Autocomplete<Tag, true, false, true>
            multiple
            freeSolo
            options={tags}
            value={selectedTagValues}
            onKeyDown={preventEnterSubmitOnClassification}
            onChange={(_, values) => onTagsChange(values)}
            disableCloseOnSelect
            getOptionLabel={(option) => (typeof option === "string" ? option : option.nome)}
            isOptionEqualToValue={(option, value) => typeof value !== "string" && option.id === value.id}
            disabled={loadingDomains}
            fullWidth
            renderTags={(value, getTagProps) =>
              value.map((option, index) => {
                const label = typeof option === "string" ? option : option.nome;
                const key = typeof option === "string" ? option : String(option.id);
                return <Chip {...getTagProps({ index })} key={key} label={label} size="small" />;
              })
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Tags"
                fullWidth
                placeholder={selectedTagValues.length ? "" : "Selecione ou digite uma nova tag"}
                helperText={getFieldHelperText("tag_ids")}
              />
            )}
          />
        </Box>
      </Stack>
    </Box>
  );
}
