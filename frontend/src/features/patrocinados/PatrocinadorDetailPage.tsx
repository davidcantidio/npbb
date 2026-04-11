import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Snackbar,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useParams, useSearchParams } from "react-router-dom";

import {
  deleteContrapartida,
  deleteContrato,
  getPatrocinador,
  updatePatrocinador,
  upsertContrapartida,
  upsertContrato,
} from "../../services/patrocinados_local";
import type {
  Contrapartida,
  ContratoPatrocinio,
  ContratoPatrocinioInput,
  ContratoStatus,
  ContrapartidaInput,
  Patrocinador,
  PatrocinadorInput,
} from "../../types/patrocinados";
import { PatrocinadorForm } from "./PatrocinadorForm";
import { emptyContratoInput, emptyContrapartidaInput } from "./defaults";

const TAB_KEYS = ["cadastro", "contrapartidas", "contratos"] as const;

function tabIndexFromSearch(tabParam: string | null): number {
  if (!tabParam) return 0;
  const idx = TAB_KEYS.indexOf(tabParam as (typeof TAB_KEYS)[number]);
  return idx >= 0 ? idx : 0;
}

function patrocinadorToInput(p: Patrocinador): PatrocinadorInput {
  return {
    nome_fantasia: p.nome_fantasia,
    razao_social: p.razao_social,
    cnpj: p.cnpj,
    email: p.email,
    telefone: p.telefone,
    site: p.site,
    observacoes: p.observacoes,
    ativo: p.ativo,
  };
}

export default function PatrocinadorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tabIndex = useMemo(() => tabIndexFromSearch(tabParam), [tabParam]);

  const [entity, setEntity] = useState<Patrocinador | null | undefined>(undefined);
  const [cadastro, setCadastro] = useState<PatrocinadorInput>(() => ({
    nome_fantasia: "",
    razao_social: "",
    cnpj: "",
    email: "",
    telefone: "",
    site: "",
    observacoes: "",
    ativo: true,
  }));
  const [snack, setSnack] = useState<{ message: string; severity: "success" | "error" } | null>(
    null,
  );

  const reload = useCallback(() => {
    if (!id) {
      setEntity(null);
      return;
    }
    const p = getPatrocinador(id);
    setEntity(p ?? null);
    if (p) setCadastro(patrocinadorToInput(p));
  }, [id]);

  useEffect(() => {
    reload();
  }, [reload]);

  const handleTabChange = (_: React.SyntheticEvent, next: number) => {
    const key = TAB_KEYS[next] ?? "cadastro";
    setSearchParams({ tab: key }, { replace: true });
  };

  const handleSaveCadastro = () => {
    if (!id || !entity) return;
    if (!cadastro.nome_fantasia.trim()) {
      setSnack({ message: "Informe o nome fantasia.", severity: "error" });
      return;
    }
    const updated = updatePatrocinador(id, cadastro);
    if (!updated) {
      setSnack({ message: "Não foi possível salvar.", severity: "error" });
      return;
    }
    setEntity(updated);
    setSnack({ message: "Cadastro atualizado.", severity: "success" });
  };

  if (!id) {
    return (
      <Alert severity="error">Identificador inválido.</Alert>
    );
  }

  if (entity === undefined) {
    return (
      <Stack spacing={2}>
        <Button component={RouterLink} to="/patrocinados" startIcon={<ArrowBackRoundedIcon />}>
          Voltar à lista
        </Button>
        <Alert severity="info">Carregando…</Alert>
      </Stack>
    );
  }

  if (entity === null) {
    return (
      <Stack spacing={2}>
        <Button component={RouterLink} to="/patrocinados" startIcon={<ArrowBackRoundedIcon />}>
          Voltar à lista
        </Button>
        <Alert severity="error">Patrocinador não encontrado.</Alert>
      </Stack>
    );
  }

  return (
    <PatrocinadorDetailInner
      id={id}
      entity={entity}
      setEntity={setEntity}
      reload={reload}
      cadastro={cadastro}
      setCadastro={setCadastro}
      tabIndex={tabIndex}
      onTabChange={handleTabChange}
      onSaveCadastro={handleSaveCadastro}
      snack={snack}
      setSnack={setSnack}
    />
  );
}

type InnerProps = {
  id: string;
  entity: Patrocinador;
  setEntity: (p: Patrocinador | null) => void;
  reload: () => void;
  cadastro: PatrocinadorInput;
  setCadastro: (v: PatrocinadorInput) => void;
  tabIndex: number;
  onTabChange: (e: React.SyntheticEvent, v: number) => void;
  onSaveCadastro: () => void;
  snack: { message: string; severity: "success" | "error" } | null;
  setSnack: (v: { message: string; severity: "success" | "error" } | null) => void;
};

function PatrocinadorDetailInner({
  id,
  entity,
  setEntity,
  reload,
  cadastro,
  setCadastro,
  tabIndex,
  onTabChange,
  onSaveCadastro,
  snack,
  setSnack,
}: InnerProps) {
  const [contraDialog, setContraDialog] = useState<{
    mode: "create" | "edit";
    values: ContrapartidaInput;
    id: string | null;
  } | null>(null);
  const [contraDelete, setContraDelete] = useState<Contrapartida | null>(null);

  const [contratoDialog, setContratoDialog] = useState<{
    mode: "create" | "edit";
    values: ContratoPatrocinioInput;
    id: string | null;
  } | null>(null);
  const [contratoDelete, setContratoDelete] = useState<ContratoPatrocinio | null>(null);

  const openNewContrapartida = () => {
    setContraDialog({ mode: "create", values: emptyContrapartidaInput(), id: null });
  };

  const openEditContrapartida = (c: Contrapartida) => {
    setContraDialog({
      mode: "edit",
      id: c.id,
      values: {
        titulo: c.titulo,
        descricao: c.descricao,
        categoria: c.categoria,
        quantidade: c.quantidade,
        valor_estimado: c.valor_estimado,
        prazo_ou_cumprimento: c.prazo_ou_cumprimento,
      },
    });
  };

  const saveContrapartida = () => {
    if (!contraDialog) return;
    if (!contraDialog.values.titulo.trim()) {
      setSnack({ message: "Informe o título da contrapartida.", severity: "error" });
      return;
    }
    upsertContrapartida(id, contraDialog.id, contraDialog.values);
    setContraDialog(null);
    reload();
    const next = getPatrocinador(id);
    if (next) setEntity(next);
    setSnack({ message: "Contrapartida salva.", severity: "success" });
  };

  const confirmDeleteContrapartida = () => {
    if (!contraDelete) return;
    deleteContrapartida(id, contraDelete.id);
    setContraDelete(null);
    reload();
    const next = getPatrocinador(id);
    if (next) setEntity(next);
    setSnack({ message: "Contrapartida removida.", severity: "success" });
  };

  const openNewContrato = () => {
    setContratoDialog({ mode: "create", values: emptyContratoInput(), id: null });
  };

  const openEditContrato = (c: ContratoPatrocinio) => {
    setContratoDialog({
      mode: "edit",
      id: c.id,
      values: {
        numero: c.numero,
        titulo: c.titulo,
        data_inicio: c.data_inicio,
        data_fim: c.data_fim,
        valor: c.valor,
        status: c.status,
        observacoes: c.observacoes,
        arquivo_nome: c.arquivo_nome,
        arquivo_url: c.arquivo_url,
      },
    });
  };

  const saveContrato = () => {
    if (!contratoDialog) return;
    if (!contratoDialog.values.titulo.trim()) {
      setSnack({ message: "Informe o título do contrato.", severity: "error" });
      return;
    }
    upsertContrato(id, contratoDialog.id, contratoDialog.values);
    setContratoDialog(null);
    reload();
    const next = getPatrocinador(id);
    if (next) setEntity(next);
    setSnack({ message: "Contrato salvo.", severity: "success" });
  };

  const confirmDeleteContrato = () => {
    if (!contratoDelete) return;
    deleteContrato(id, contratoDelete.id);
    setContratoDelete(null);
    reload();
    const next = getPatrocinador(id);
    if (next) setEntity(next);
    setSnack({ message: "Contrato removido.", severity: "success" });
  };

  return (
    <Stack spacing={2}>
      <Alert severity="info">
        Os dados desta tela são armazenados apenas no seu navegador (localStorage) até a API de
        patrocinadores estar disponível.
      </Alert>

      <Box sx={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 2 }}>
        <Button
          component={RouterLink}
          to="/patrocinados"
          startIcon={<ArrowBackRoundedIcon />}
          color="inherit"
        >
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          {entity.nome_fantasia || "Patrocinador"}
        </Typography>
      </Box>

      <Paper variant="outlined">
        <Tabs value={tabIndex} onChange={onTabChange} variant="scrollable" scrollButtons="auto">
          <Tab label="Cadastro" id="patroc-tab-0" aria-controls="patroc-panel-0" />
          <Tab label="Contrapartidas" id="patroc-tab-1" aria-controls="patroc-panel-1" />
          <Tab label="Contratos" id="patroc-tab-2" aria-controls="patroc-panel-2" />
        </Tabs>

        <Box role="tabpanel" hidden={tabIndex !== 0} id="patroc-panel-0" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={onSaveCadastro}>
                Salvar cadastro
              </Button>
            </Box>
            <PatrocinadorForm value={cadastro} onChange={setCadastro} />
          </Stack>
        </Box>

        <Box role="tabpanel" hidden={tabIndex !== 1} id="patroc-panel-1" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button variant="outlined" startIcon={<AddRoundedIcon />} onClick={openNewContrapartida}>
                Nova contrapartida
              </Button>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Título</TableCell>
                    <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>Categoria</TableCell>
                    <TableCell align="right">Ações</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entity.contrapartidas.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3}>
                        <Typography color="text.secondary">Nenhuma contrapartida cadastrada.</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    entity.contrapartidas.map((c) => (
                      <TableRow key={c.id}>
                        <TableCell>
                          <Typography fontWeight={600}>{c.titulo}</Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            {c.descricao ? `${c.descricao.slice(0, 80)}${c.descricao.length > 80 ? "…" : ""}` : "—"}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>
                          {c.categoria || "—"}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Editar">
                            <IconButton size="small" onClick={() => openEditContrapartida(c)}>
                              <EditOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Excluir">
                            <IconButton size="small" color="error" onClick={() => setContraDelete(c)}>
                              <DeleteOutlineIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Stack>
        </Box>

        <Box role="tabpanel" hidden={tabIndex !== 2} id="patroc-panel-2" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button variant="outlined" startIcon={<AddRoundedIcon />} onClick={openNewContrato}>
                Novo contrato
              </Button>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Título / número</TableCell>
                    <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>Vigência</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Ações</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entity.contratos.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4}>
                        <Typography color="text.secondary">Nenhum contrato cadastrado.</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    entity.contratos.map((c) => (
                      <TableRow key={c.id}>
                        <TableCell>
                          <Typography fontWeight={600}>{c.titulo}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {c.numero || "—"}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>
                          {c.data_inicio || "—"} → {c.data_fim || "—"}
                        </TableCell>
                        <TableCell>{c.status}</TableCell>
                        <TableCell align="right">
                          <Tooltip title="Editar">
                            <IconButton size="small" onClick={() => openEditContrato(c)}>
                              <EditOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Excluir">
                            <IconButton size="small" color="error" onClick={() => setContratoDelete(c)}>
                              <DeleteOutlineIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Stack>
        </Box>
      </Paper>

      <Dialog open={Boolean(contraDialog)} onClose={() => setContraDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{contraDialog?.mode === "edit" ? "Editar contrapartida" : "Nova contrapartida"}</DialogTitle>
        <DialogContent>
          {contraDialog ? (
            <Stack spacing={2} sx={{ pt: 1 }}>
              <TextField
                label="Título"
                value={contraDialog.values.titulo}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, titulo: e.target.value },
                  })
                }
                required
                fullWidth
              />
              <TextField
                label="Descrição"
                value={contraDialog.values.descricao}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, descricao: e.target.value },
                  })
                }
                multiline
                minRows={2}
                fullWidth
              />
              <TextField
                label="Categoria"
                value={contraDialog.values.categoria}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, categoria: e.target.value },
                  })
                }
                fullWidth
              />
              <TextField
                label="Quantidade"
                value={contraDialog.values.quantidade}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, quantidade: e.target.value },
                  })
                }
                fullWidth
              />
              <TextField
                label="Valor estimado"
                value={contraDialog.values.valor_estimado}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, valor_estimado: e.target.value },
                  })
                }
                fullWidth
              />
              <TextField
                label="Prazo ou cumprimento"
                value={contraDialog.values.prazo_ou_cumprimento}
                onChange={(e) =>
                  setContraDialog({
                    ...contraDialog,
                    values: { ...contraDialog.values, prazo_ou_cumprimento: e.target.value },
                  })
                }
                multiline
                minRows={2}
                fullWidth
              />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContraDialog(null)}>Cancelar</Button>
          <Button variant="contained" onClick={saveContrapartida}>
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(contraDelete)} onClose={() => setContraDelete(null)}>
        <DialogTitle>Remover contrapartida?</DialogTitle>
        <DialogContent>
          <Typography>Esta ação não pode ser desfeita.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContraDelete(null)}>Cancelar</Button>
          <Button color="error" variant="contained" onClick={confirmDeleteContrapartida}>
            Remover
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(contratoDialog)} onClose={() => setContratoDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{contratoDialog?.mode === "edit" ? "Editar contrato" : "Novo contrato"}</DialogTitle>
        <DialogContent>
          {contratoDialog ? (
            <Stack spacing={2} sx={{ pt: 1 }}>
              <TextField
                label="Número"
                value={contratoDialog.values.numero}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, numero: e.target.value },
                  })
                }
                fullWidth
              />
              <TextField
                label="Título"
                value={contratoDialog.values.titulo}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, titulo: e.target.value },
                  })
                }
                required
                fullWidth
              />
              <TextField
                label="Data início"
                type="date"
                value={contratoDialog.values.data_inicio}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, data_inicio: e.target.value },
                  })
                }
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
              <TextField
                label="Data fim"
                type="date"
                value={contratoDialog.values.data_fim}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, data_fim: e.target.value },
                  })
                }
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
              <TextField
                label="Valor"
                value={contratoDialog.values.valor}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, valor: e.target.value },
                  })
                }
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel id="contrato-status-label">Status</InputLabel>
                <Select
                  labelId="contrato-status-label"
                  label="Status"
                  value={contratoDialog.values.status}
                  onChange={(e) =>
                    setContratoDialog({
                      ...contratoDialog,
                      values: { ...contratoDialog.values, status: e.target.value as ContratoStatus },
                    })
                  }
                >
                  <MenuItem value="rascunho">Rascunho</MenuItem>
                  <MenuItem value="ativo">Ativo</MenuItem>
                  <MenuItem value="encerrado">Encerrado</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Observações"
                value={contratoDialog.values.observacoes}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, observacoes: e.target.value },
                  })
                }
                multiline
                minRows={2}
                fullWidth
              />
              <TextField
                label="Nome do arquivo (referência)"
                value={contratoDialog.values.arquivo_nome}
                onChange={(e) =>
                  setContratoDialog({
                    ...contratoDialog,
                    values: { ...contratoDialog.values, arquivo_nome: e.target.value },
                  })
                }
                helperText="Upload de arquivo será suportado quando a API estiver pronta."
                fullWidth
              />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContratoDialog(null)}>Cancelar</Button>
          <Button variant="contained" onClick={saveContrato}>
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(contratoDelete)} onClose={() => setContratoDelete(null)}>
        <DialogTitle>Remover contrato?</DialogTitle>
        <DialogContent>
          <Typography>Esta ação não pode ser desfeita.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContratoDelete(null)}>Cancelar</Button>
          <Button color="error" variant="contained" onClick={confirmDeleteContrato}>
            Remover
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={Boolean(snack)}
        autoHideDuration={4000}
        onClose={() => setSnack(null)}
        message={snack?.message}
      />
    </Stack>
  );
}
