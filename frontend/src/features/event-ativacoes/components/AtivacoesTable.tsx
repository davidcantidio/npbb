import {
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";

import type { Ativacao } from "../../../services/eventos";

export type AtivacoesTableProps = {
  ativacoes: Ativacao[];
  gamificacaoNameById: Map<number, string>;
  canAct: boolean;
  isBusy: boolean;
  onEdit: (item: Ativacao) => void;
  onView: (item: Ativacao) => void;
  onDelete: (item: Ativacao) => void;
};

export function AtivacoesTable({
  ativacoes,
  gamificacaoNameById,
  canAct,
  isBusy,
  onEdit,
  onView,
  onDelete,
}: AtivacoesTableProps) {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Nome</TableCell>
          <TableCell>Descricao</TableCell>
          <TableCell width={160}>Tipo de conversao</TableCell>
          <TableCell width={220}>Gamificação</TableCell>
          <TableCell width={160} align="right">
            Ações
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {ativacoes.map((item) => {
          const gamificacaoLabel = item.gamificacao_id
            ? gamificacaoNameById.get(item.gamificacao_id) ?? `#${item.gamificacao_id}`
            : "Nenhuma";
          return (
            <TableRow key={item.id}>
              <TableCell>{item.nome}</TableCell>
              <TableCell>{item.descricao || "-"}</TableCell>
              <TableCell>{item.checkin_unico ? "Unica" : "Multipla"}</TableCell>
              <TableCell>{gamificacaoLabel}</TableCell>
              <TableCell align="right">
                <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                  <IconButton
                    aria-label="Editar"
                    size="small"
                    color="primary"
                    disabled={!canAct || isBusy}
                    onClick={() => onEdit(item)}
                  >
                    <EditOutlinedIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    aria-label="Visualizar"
                    size="small"
                    color="primary"
                    disabled={!canAct || isBusy}
                    onClick={() => onView(item)}
                  >
                    <VisibilityOutlinedIcon fontSize="small" />
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
          );
        })}

        {!ativacoes.length && (
          <TableRow>
            <TableCell colSpan={5}>
              <Typography variant="body2" color="text.secondary">
                Nenhuma ativação adicionada.
              </Typography>
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
