import { useState } from "react";
import {
  Box,
  Button,
  FormControl,
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

import { createGroupContract } from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type { SponsorshipContractRead } from "../../../types/sponsorship";

type GroupContractsPanelProps = {
  token: string | null;
  groupId: number;
  contracts: SponsorshipContractRead[];
  selectedContractId: number | null;
  onSelectContract: (contractId: number | null) => void;
  onChanged: () => void;
  onError: (message: string) => void;
};

export default function GroupContractsPanel({
  token,
  groupId,
  contracts,
  selectedContractId,
  onSelectContract,
  onChanged,
  onError,
}: GroupContractsPanelProps) {
  const [contractNumber, setContractNumber] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [status, setStatus] = useState<"active" | "inactive" | "archived">("active");
  const [originalFilename, setOriginalFilename] = useState("");
  const [fileStorageKey, setFileStorageKey] = useState("");
  const [fileChecksum, setFileChecksum] = useState("");

  const handleCreate = async () => {
    if (!token) return;
    if (!contractNumber.trim() || !startDate || !endDate) {
      onError("Informe numero e vigencia do contrato.");
      return;
    }
    const normalizedOriginalFilename = originalFilename.trim();
    const normalizedFileStorageKey = fileStorageKey.trim();
    const normalizedFileChecksum = fileChecksum.trim();
    const hasFileMetadata = Boolean(
      normalizedOriginalFilename || normalizedFileStorageKey || normalizedFileChecksum,
    );
    try {
      await createGroupContract(token, groupId, {
        group_id: groupId,
        contract_number: contractNumber.trim(),
        start_date: startDate,
        end_date: endDate,
        status,
        original_filename: normalizedOriginalFilename || null,
        file_storage_key: normalizedFileStorageKey || null,
        file_checksum: normalizedFileChecksum || null,
        uploaded_at: hasFileMetadata ? new Date().toISOString() : null,
      });
      setContractNumber("");
      setStartDate("");
      setEndDate("");
      setStatus("active");
      setOriginalFilename("");
      setFileStorageKey("");
      setFileChecksum("");
      onChanged();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel criar o contrato."));
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1" fontWeight={800}>
        Novo contrato
      </Typography>
      <TextField label="Numero do contrato" value={contractNumber} onChange={(e) => setContractNumber(e.target.value)} fullWidth />
      <TextField label="Data inicio" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
      <TextField label="Data fim" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
      <TextField
        label="Nome original do arquivo"
        value={originalFilename}
        onChange={(e) => setOriginalFilename(e.target.value)}
        fullWidth
      />
      <TextField
        label="Chave de storage"
        value={fileStorageKey}
        onChange={(e) => setFileStorageKey(e.target.value)}
        fullWidth
      />
      <TextField
        label="Checksum do arquivo"
        value={fileChecksum}
        onChange={(e) => setFileChecksum(e.target.value)}
        fullWidth
      />
      <FormControl fullWidth>
        <InputLabel id="group-contract-status-label">Status</InputLabel>
        <Select
          labelId="group-contract-status-label"
          value={status}
          label="Status"
          onChange={(e) => setStatus(e.target.value as "active" | "inactive" | "archived")}
        >
          <MenuItem value="active">active</MenuItem>
          <MenuItem value="inactive">inactive</MenuItem>
          <MenuItem value="archived">archived</MenuItem>
        </Select>
      </FormControl>
      <Box>
        <Button variant="contained" onClick={() => void handleCreate()}>
          Criar contrato
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Numero</TableCell>
              <TableCell>Vigencia</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Arquivo</TableCell>
              <TableCell align="center">Clausulas</TableCell>
              <TableCell align="center">Contrapartidas</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {contracts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography color="text.secondary">Nenhum contrato cadastrado.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              contracts.map((contract) => (
                <TableRow
                  key={contract.id}
                  selected={selectedContractId === contract.id}
                  hover
                  onClick={() => onSelectContract(contract.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell>{contract.contract_number}</TableCell>
                  <TableCell>
                    {contract.start_date} ate {contract.end_date}
                  </TableCell>
                  <TableCell>{contract.status}</TableCell>
                  <TableCell>{contract.original_filename || "Sem arquivo"}</TableCell>
                  <TableCell align="center">{contract.clauses_count}</TableCell>
                  <TableCell align="center">{contract.requirements_count}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
