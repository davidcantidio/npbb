import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
} from "@mui/material";
import { LeadListItem } from "../../../services/leads_import";

type LeadListTableProps = {
  leads: LeadListItem[];
  leadsTotal: number;
  leadsLoading: boolean;
  leadsError: string | null;
  leadsPage: number;
  leadsPageSize: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (pageSize: number) => void;
  onRefresh: () => void;
};

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString("pt-BR");
}

function formatCpf(value: string | null | undefined): string {
  if (!value) return "-";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length !== 11) return value;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

/**
 * Renders paginated table with imported leads.
 */
export function LeadListTable({
  leads,
  leadsTotal,
  leadsLoading,
  leadsError,
  leadsPage,
  leadsPageSize,
  onPageChange,
  onRowsPerPageChange,
  onRefresh,
}: LeadListTableProps) {
  return (
    <>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        spacing={1}
        sx={{ px: { xs: 2, md: 3 }, py: 2 }}
      >
        <Box>
          <Typography variant="subtitle1" fontWeight={800}>
            Leads cadastrados
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total no banco: {leadsTotal}
          </Typography>
        </Box>
        <Button variant="outlined" sx={{ textTransform: "none", fontWeight: 700 }} onClick={onRefresh} disabled={leadsLoading}>
          Atualizar
        </Button>
      </Stack>

      {leadsError ? <Alert severity="error" sx={{ mx: { xs: 2, md: 3 }, mb: 2 }}>{leadsError}</Alert> : null}

      <TableContainer>
        <Table size="small" aria-label="Tabela de leads">
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Contato</TableCell>
              <TableCell>CPF</TableCell>
              <TableCell>Evento (origem)</TableCell>
              <TableCell>Evento convertido</TableCell>
              <TableCell>Conversao</TableCell>
              <TableCell>Data da compra</TableCell>
              <TableCell>Cadastro</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {leadsLoading && leads.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ py: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2" color="text.secondary">
                      Carregando leads...
                    </Typography>
                  </Stack>
                </TableCell>
              </TableRow>
            ) : null}

            {!leadsLoading && leads.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8}>
                  <Typography variant="body2" color="text.secondary">
                    Nenhum lead encontrado.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : null}

            {leads.map((lead) => (
              <TableRow key={lead.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight={600}>
                    {lead.nome || "-"}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{lead.email || "-"}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {lead.telefone || "-"}
                  </Typography>
                </TableCell>
                <TableCell>{formatCpf(lead.cpf)}</TableCell>
                <TableCell>
                  <Typography variant="body2">{lead.evento_nome || "-"}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {[lead.cidade, lead.estado].filter(Boolean).join(" / ") || "-"}
                  </Typography>
                </TableCell>
                <TableCell>
                  {lead.evento_convertido_nome ||
                    (lead.evento_convertido_id ? `#${lead.evento_convertido_id}` : "-")}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {lead.tipo_conversao ? lead.tipo_conversao.replace(/_/g, " ") : "-"}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDateTime(lead.data_conversao)}
                  </Typography>
                </TableCell>
                <TableCell>{formatDateTime(lead.data_compra)}</TableCell>
                <TableCell>{formatDateTime(lead.data_criacao)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={leadsTotal}
        page={Math.max(leadsPage - 1, 0)}
        onPageChange={(_, page) => onPageChange(page + 1)}
        rowsPerPage={leadsPageSize}
        onRowsPerPageChange={(event) => onRowsPerPageChange(Number(event.target.value))}
        rowsPerPageOptions={[10, 20, 50]}
        labelRowsPerPage="Linhas por pagina"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`}
      />
    </>
  );
}
