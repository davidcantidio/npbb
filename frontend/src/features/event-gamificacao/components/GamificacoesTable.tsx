import {
  Box,
  CircularProgress,
  Divider,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import { Stack } from "@mui/material";

import type { Gamificacao } from "../../../services/eventos";

export type GamificacoesTableProps = {
  gamificacoes: Gamificacao[];
  loading: boolean;
  canAct: boolean;
  isBusy: boolean;
  onEdit: (item: Gamificacao) => void;
  onDelete: (item: Gamificacao) => void;
};

export function GamificacoesTable({
  gamificacoes,
  loading,
  canAct,
  isBusy,
  onEdit,
  onDelete,
}: GamificacoesTableProps) {
  return (
    <Paper elevation={2} sx={{ borderRadius: 1, overflow: "hidden", width: "100%", flex: 1 }}>
      <Box sx={{ px: 2.5, py: 2 }}>
        <Typography variant="h6" fontWeight={900}>
          Gamificações adicionadas
        </Typography>
      </Box>
      <Divider />

      {loading ? (
        <Box
          sx={{
            p: 4,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1,
          }}
        >
          <CircularProgress size={22} />
          <Typography variant="body2" color="text.secondary">
            Carregando...
          </Typography>
        </Box>
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell width={220}>Prêmio</TableCell>
              <TableCell width={120} align="right">
                Ações
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {gamificacoes.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.nome}</TableCell>
                <TableCell>{item.premio}</TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                    <IconButton
                      aria-label="Editar"
                      size="small"
                      disabled={!canAct || isBusy}
                      onClick={() => onEdit(item)}
                    >
                      <EditOutlinedIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      aria-label="Excluir"
                      size="small"
                      color="error"
                      disabled={!canAct || isBusy}
                      onClick={() => onDelete(item)}
                    >
                      <DeleteOutlineOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}

            {!gamificacoes.length && (
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography variant="body2" color="text.secondary">
                    Nenhuma gamificação adicionada.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </Paper>
  );
}
