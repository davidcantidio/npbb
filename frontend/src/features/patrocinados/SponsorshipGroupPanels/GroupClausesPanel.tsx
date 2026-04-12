import { useCallback, useEffect, useState } from "react";
import {
  Box,
  Button,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";

import {
  createContractClause,
  deleteContractClause,
  listContractClauses,
} from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type { ContractClauseRead, SponsorshipContractRead } from "../../../types/sponsorship";

type GroupClausesPanelProps = {
  token: string | null;
  contracts: SponsorshipContractRead[];
  selectedContractId: number | null;
  onSelectContract: (contractId: number | null) => void;
  onError: (message: string) => void;
};

export default function GroupClausesPanel({
  token,
  contracts,
  selectedContractId,
  onSelectContract,
  onError,
}: GroupClausesPanelProps) {
  const [clauses, setClauses] = useState<ContractClauseRead[]>([]);
  const [clauseIdentifier, setClauseIdentifier] = useState("");
  const [title, setTitle] = useState("");
  const [clauseText, setClauseText] = useState("");
  const [displayOrder, setDisplayOrder] = useState("0");
  const [pageReference, setPageReference] = useState("");

  const load = useCallback(async () => {
    if (!token || selectedContractId == null) {
      setClauses([]);
      return;
    }
    try {
      const data = await listContractClauses(token, selectedContractId);
      setClauses(data);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar as clausulas."));
    }
  }, [onError, selectedContractId, token]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleCreate = async () => {
    if (!token || selectedContractId == null) return;
    if (!clauseIdentifier.trim()) {
      onError("Informe o identificador da clausula.");
      return;
    }
    try {
      await createContractClause(token, selectedContractId, {
        clause_identifier: clauseIdentifier.trim(),
        title: title.trim() || null,
        clause_text: clauseText.trim() || null,
        display_order: Number(displayOrder || "0"),
        page_reference: pageReference.trim() || null,
      });
      setClauseIdentifier("");
      setTitle("");
      setClauseText("");
      setDisplayOrder("0");
      setPageReference("");
      await load();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel criar a clausula."));
    }
  };

  const handleDelete = async (clauseId: number) => {
    if (!token || selectedContractId == null) return;
    try {
      await deleteContractClause(token, selectedContractId, clauseId);
      await load();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover a clausula."));
    }
  };

  return (
    <Stack spacing={2}>
      <FormControl fullWidth>
        <InputLabel id="clauses-contract-label">Contrato</InputLabel>
        <Select
          labelId="clauses-contract-label"
          value={selectedContractId == null ? "" : String(selectedContractId)}
          label="Contrato"
          onChange={(e) => onSelectContract(e.target.value ? Number(e.target.value) : null)}
        >
          {contracts.map((contract) => (
            <MenuItem key={contract.id} value={String(contract.id)}>
              {contract.contract_number}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Typography variant="subtitle1" fontWeight={800}>
        Nova clausula
      </Typography>
      <TextField label="Identificador" value={clauseIdentifier} onChange={(e) => setClauseIdentifier(e.target.value)} fullWidth />
      <TextField label="Titulo" value={title} onChange={(e) => setTitle(e.target.value)} fullWidth />
      <TextField label="Texto" value={clauseText} onChange={(e) => setClauseText(e.target.value)} multiline minRows={3} fullWidth />
      <TextField label="Ordem" value={displayOrder} onChange={(e) => setDisplayOrder(e.target.value)} fullWidth />
      <TextField label="Pagina" value={pageReference} onChange={(e) => setPageReference(e.target.value)} fullWidth />
      <Box>
        <Button variant="contained" disabled={selectedContractId == null} onClick={() => void handleCreate()}>
          Criar clausula
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Identificador</TableCell>
              <TableCell>Titulo</TableCell>
              <TableCell>Pagina</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {clauses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary">Nenhuma clausula cadastrada.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              clauses.map((clause) => (
                <TableRow key={clause.id}>
                  <TableCell>{clause.clause_identifier}</TableCell>
                  <TableCell>{clause.title || "-"}</TableCell>
                  <TableCell>{clause.page_reference || "-"}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={() => void handleDelete(clause.id)}>
                      <DeleteOutlineIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
