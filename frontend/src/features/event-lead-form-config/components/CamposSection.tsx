import { useState } from "react";
import type { DragEndEvent } from "@dnd-kit/core";
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import DragIndicatorRoundedIcon from "@mui/icons-material/DragIndicatorRounded";
import { Box, Button, Checkbox, Collapse, FormControlLabel, IconButton, Stack, Typography } from "@mui/material";

type CamposSectionProps = {
  camposAtivosOrdenados: string[];
  camposDisponiveis: string[];
  camposAtivos: Set<string>;
  camposObrigatorios: Record<string, boolean>;
  isCampoSempreObrigatorio: (nome: string) => boolean;
  onToggleCampo: (nome: string) => void;
  onSetObrigatorio: (nome: string, obrigatorio: boolean) => void;
  onReorderCampo: (activeNome: string, overNome: string) => void;
};

function slugifyCampoNome(nome: string) {
  return nome.toLowerCase().replace(/\s+/g, "-");
}

type SortableCampoCardProps = {
  nome: string;
  ativo: boolean;
  obrigatorio: boolean;
  campoTravado: boolean;
  onToggleCampo: (nome: string) => void;
  onSetObrigatorio: (nome: string, obrigatorio: boolean) => void;
};

function SortableCampoCard({
  nome,
  ativo,
  obrigatorio,
  campoTravado,
  onToggleCampo,
  onSetObrigatorio,
}: SortableCampoCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: nome,
  });

  return (
    <Box
      ref={setNodeRef}
      data-testid={`lead-field-card-${slugifyCampoNome(nome)}`}
      sx={{
        px: 1.5,
        py: 1,
        borderRadius: 2,
        border: 1,
        borderColor: "divider",
        backgroundColor: ativo ? "rgba(103, 80, 164, 0.05)" : "transparent",
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.72 : 1,
      }}
    >
      <Stack
        direction={{ xs: "column", sm: "row" }}
        alignItems={{ xs: "flex-start", sm: "center" }}
        justifyContent="space-between"
        gap={1.5}
      >
        <Stack direction="row" spacing={1.25} alignItems="center">
          <IconButton
            size="small"
            aria-label={`Reordenar campo ${nome}`}
            data-testid={`lead-field-drag-${slugifyCampoNome(nome)}`}
            sx={{ cursor: "grab", touchAction: "none" }}
            {...attributes}
            {...listeners}
          >
            <DragIndicatorRoundedIcon fontSize="small" />
          </IconButton>

          <Box>
            <Typography variant="body2" fontWeight={800} lineHeight={1.2}>
              {nome}
            </Typography>
            {campoTravado ? (
              <Typography variant="caption" color="text.secondary">
                Campo obrigatório por padrão.
              </Typography>
            ) : null}
          </Box>
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
          <FormControlLabel
            sx={{ m: 0 }}
            control={
              <Checkbox
                size="small"
                checked={ativo}
                disabled={campoTravado}
                onChange={() => onToggleCampo(nome)}
              />
            }
            label="Ativo"
          />
          <FormControlLabel
            sx={{ m: 0 }}
            control={
              <Checkbox
                size="small"
                checked={obrigatorio}
                disabled={!ativo || campoTravado}
                onChange={(_, checked) => onSetObrigatorio(nome, checked)}
              />
            }
            label="Obrigatório"
          />
        </Stack>
      </Stack>
    </Box>
  );
}

export function CamposSection({
  camposAtivosOrdenados,
  camposDisponiveis,
  camposAtivos,
  camposObrigatorios,
  isCampoSempreObrigatorio,
  onToggleCampo,
  onSetObrigatorio,
  onReorderCampo,
}: CamposSectionProps) {
  const [showCamposDisponiveis, setShowCamposDisponiveis] = useState(false);
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = ({ active, over }: DragEndEvent) => {
    if (!over || active.id === over.id) return;
    onReorderCampo(String(active.id), String(over.id));
  };

  return (
    <>
      <Box>
        <Typography variant="subtitle1" fontWeight={900} gutterBottom>
          Campos possíveis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Os campos ativos aparecem em uma lista única. Use o botão &quot;+&quot; para revelar
          opções adicionais; o preview responde imediatamente e &quot;Salvar&quot; persiste a
          configuração.
        </Typography>
      </Box>

      {camposAtivosOrdenados.length || camposDisponiveis.length ? (
        <Stack spacing={1.25}>
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext
              items={camposAtivosOrdenados}
              strategy={verticalListSortingStrategy}
            >
              <Stack spacing={1.25}>
                {camposAtivosOrdenados.map((nome) => {
                  const ativo = camposAtivos.has(nome);
                  const obrigatorio = ativo ? (camposObrigatorios[nome] ?? true) : false;

                  return (
                    <SortableCampoCard
                      key={nome}
                      nome={nome}
                      ativo={ativo}
                      obrigatorio={obrigatorio}
                      campoTravado={isCampoSempreObrigatorio(nome)}
                      onToggleCampo={onToggleCampo}
                      onSetObrigatorio={onSetObrigatorio}
                    />
                  );
                })}
              </Stack>
            </SortableContext>
          </DndContext>

          {camposDisponiveis.length ? (
            <>
              <Button
                variant="outlined"
                color="inherit"
                startIcon={<AddRoundedIcon />}
                onClick={() => setShowCamposDisponiveis((prev) => !prev)}
                sx={{ alignSelf: "flex-start", borderRadius: 999 }}
              >
                {showCamposDisponiveis ? "Ocultar campos" : "Adicionar campo"}
              </Button>

              <Collapse in={showCamposDisponiveis}>
                <Stack spacing={1.25} sx={{ pt: 0.5 }}>
                  {camposDisponiveis.map((nome) => (
                    <Box
                      key={nome}
                      data-testid={`lead-field-option-${slugifyCampoNome(nome)}`}
                      sx={{
                        px: 1.5,
                        py: 1,
                        borderRadius: 2,
                        border: 1,
                        borderStyle: "dashed",
                        borderColor: "divider",
                        backgroundColor: "background.default",
                      }}
                    >
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        alignItems={{ xs: "flex-start", sm: "center" }}
                        justifyContent="space-between"
                        gap={1.5}
                      >
                        <Typography variant="body2" fontWeight={700}>
                          {nome}
                        </Typography>

                        <FormControlLabel
                          sx={{ m: 0 }}
                          control={
                            <Checkbox
                              size="small"
                              checked={false}
                              onChange={() => onToggleCampo(nome)}
                            />
                          }
                          label="Ativo"
                        />
                      </Stack>
                    </Box>
                  ))}
                </Stack>
              </Collapse>
            </>
          ) : null}
        </Stack>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum campo disponível.
        </Typography>
      )}
    </>
  );
}
