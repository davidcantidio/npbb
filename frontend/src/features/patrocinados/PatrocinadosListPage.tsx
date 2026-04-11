import { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  Paper,
  Snackbar,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { deletePatrocinador, listPatrocinadores } from "../../services/patrocinados_local";
import type { PatrocinadorListItem } from "../../types/patrocinados";

function normalizeSearch(s: string) {
  return s.trim().toLowerCase();
}

export default function PatrocinadosListPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<PatrocinadorListItem[]>(() => listPatrocinadores());
  const [search, setSearch] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<PatrocinadorListItem | null>(null);
  const [snack, setSnack] = useState<{ message: string; severity: "success" | "error" } | null>(
    null,
  );

  const refresh = () => setItems(listPatrocinadores());

  const filtered = useMemo(() => {
    const q = normalizeSearch(search);
    if (!q) return items;
    return items.filter(
      (p) =>
        normalizeSearch(p.nome_fantasia).includes(q) ||
        normalizeSearch(p.razao_social).includes(q) ||
        normalizeSearch(p.cnpj).includes(q) ||
        normalizeSearch(p.email).includes(q),
    );
  }, [items, search]);

  const handleConfirmDelete = () => {
    if (!deleteTarget) return;
    const ok = deletePatrocinador(deleteTarget.id);
    setDeleteTarget(null);
    if (ok) {
      refresh();
      setSnack({ message: "Patrocinador removido.", severity: "success" });
    } else {
      setSnack({ message: "Não foi possível remover.", severity: "error" });
    }
  };

  return (
    <Stack spacing={2}>
      <Alert severity="info">
        Os dados desta tela são armazenados apenas no seu navegador (localStorage) até a API de
        patrocinadores estar disponível.
      </Alert>

      <Box sx={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 2 }}>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Patrocinados
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddRoundedIcon />}
          onClick={() => navigate("/patrocinados/novo")}
        >
          Novo patrocinador
        </Button>
      </Box>

      <TextField
        placeholder="Buscar por nome, razão social, CNPJ ou e-mail"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        fullWidth
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchRoundedIcon fontSize="small" color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Nome fantasia</TableCell>
              <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>CNPJ</TableCell>
              <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>E-mail</TableCell>
              <TableCell align="center">Contrapartidas</TableCell>
              <TableCell align="center">Contratos</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography color="text.secondary" sx={{ py: 2 }}>
                    {items.length === 0
                      ? "Nenhum patrocinador cadastrado. Clique em Novo patrocinador para começar."
                      : "Nenhum resultado para a busca."}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <Typography fontWeight={700}>{row.nome_fantasia || "—"}</Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {row.ativo ? "Ativo" : "Inativo"}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ display: { xs: "none", md: "table-cell" } }}>{row.cnpj || "—"}</TableCell>
                  <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>{row.email || "—"}</TableCell>
                  <TableCell align="center">{row.contrapartidas_count}</TableCell>
                  <TableCell align="center">{row.contratos_count}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="Abrir detalhe">
                      <IconButton
                        component={RouterLink}
                        to={`/patrocinados/${row.id}`}
                        size="small"
                        color="primary"
                        aria-label={`Abrir ${row.nome_fantasia}`}
                      >
                        <OpenInNewRoundedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Editar cadastro">
                      <IconButton
                        component={RouterLink}
                        to={`/patrocinados/${row.id}?tab=cadastro`}
                        size="small"
                        aria-label={`Editar ${row.nome_fantasia}`}
                      >
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Excluir">
                      <IconButton
                        size="small"
                        color="error"
                        aria-label={`Excluir ${row.nome_fantasia}`}
                        onClick={() => setDeleteTarget(row)}
                      >
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

      <Dialog open={Boolean(deleteTarget)} onClose={() => setDeleteTarget(null)}>
        <DialogTitle>Excluir patrocinador?</DialogTitle>
        <DialogContent>
          <Typography>
            Esta ação remove o cadastro de{" "}
            <strong>{deleteTarget?.nome_fantasia || "este patrocinador"}</strong> e todos os dados
            locais associados (contrapartidas e contratos).
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>Cancelar</Button>
          <Button color="error" variant="contained" onClick={handleConfirmDelete}>
            Excluir
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
