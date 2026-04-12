import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Switch,
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
  createContractRequirement,
  deleteContractRequirement,
  listContractClauses,
  listContractRequirements,
} from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type {
  ContractClauseRead,
  CounterpartRequirementRead,
  SponsorshipContractRead,
} from "../../../types/sponsorship";

type GroupRequirementsPanelProps = {
  token: string | null;
  contracts: SponsorshipContractRead[];
  selectedContractId: number | null;
  onSelectContract: (contractId: number | null) => void;
  onRequirementsChange: (requirements: CounterpartRequirementRead[]) => void;
  onError: (message: string) => void;
};

export default function GroupRequirementsPanel({
  token,
  contracts,
  selectedContractId,
  onSelectContract,
  onRequirementsChange,
  onError,
}: GroupRequirementsPanelProps) {
  const [clauses, setClauses] = useState<ContractClauseRead[]>([]);
  const [requirements, setRequirements] = useState<CounterpartRequirementRead[]>([]);
  const [clauseId, setClauseId] = useState("");
  const [requirementType, setRequirementType] = useState("");
  const [description, setDescription] = useState("");
  const [isRecurring, setIsRecurring] = useState(false);
  const [periodType, setPeriodType] = useState("month");
  const [periodRule, setPeriodRule] = useState("");
  const [expectedOccurrences, setExpectedOccurrences] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [responsibilityType, setResponsibilityType] = useState("individual");
  const [status, setStatus] = useState("planned");

  const clauseMap = useMemo(
    () => Object.fromEntries(clauses.map((clause) => [clause.id, clause.clause_identifier])),
    [clauses],
  );

  const load = useCallback(async () => {
    if (!token || selectedContractId == null) {
      setClauses([]);
      setRequirements([]);
      onRequirementsChange([]);
      return;
    }
    try {
      const [clausesData, requirementsData] = await Promise.all([
        listContractClauses(token, selectedContractId),
        listContractRequirements(token, selectedContractId),
      ]);
      setClauses(clausesData);
      setRequirements(requirementsData);
      onRequirementsChange(requirementsData);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar contrapartidas."));
    }
  }, [onError, onRequirementsChange, selectedContractId, token]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleCreate = async () => {
    if (!token || selectedContractId == null) return;
    if (!clauseId || !requirementType.trim() || !description.trim()) {
      onError("Informe clausula, tipo e descricao da contrapartida.");
      return;
    }
    try {
      await createContractRequirement(token, selectedContractId, {
        clause_id: Number(clauseId),
        requirement_type: requirementType.trim(),
        description: description.trim(),
        is_recurring: isRecurring,
        period_type: isRecurring ? (periodType as any) : null,
        period_rule_description: isRecurring ? periodRule.trim() || null : null,
        expected_occurrences: isRecurring && expectedOccurrences ? Number(expectedOccurrences) : null,
        recurrence_start_date: isRecurring ? startDate || null : null,
        recurrence_end_date: isRecurring ? endDate || null : null,
        responsibility_type: responsibilityType as any,
        status: status as any,
      });
      setClauseId("");
      setRequirementType("");
      setDescription("");
      setIsRecurring(false);
      setPeriodType("month");
      setPeriodRule("");
      setExpectedOccurrences("");
      setStartDate("");
      setEndDate("");
      setResponsibilityType("individual");
      setStatus("planned");
      await load();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel criar a contrapartida."));
    }
  };

  const handleDelete = async (requirementId: number) => {
    if (!token || selectedContractId == null) return;
    try {
      await deleteContractRequirement(token, selectedContractId, requirementId);
      await load();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover a contrapartida."));
    }
  };

  return (
    <Stack spacing={2}>
      <FormControl fullWidth>
        <InputLabel id="requirements-contract-label">Contrato</InputLabel>
        <Select
          labelId="requirements-contract-label"
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
      <FormControl fullWidth>
        <InputLabel id="requirements-clause-label">Clausula</InputLabel>
        <Select
          labelId="requirements-clause-label"
          value={clauseId}
          label="Clausula"
          onChange={(e) => setClauseId(String(e.target.value))}
        >
          {clauses.map((clause) => (
            <MenuItem key={clause.id} value={String(clause.id)}>
              {clause.clause_identifier}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField label="Tipo da contrapartida" value={requirementType} onChange={(e) => setRequirementType(e.target.value)} fullWidth />
      <TextField label="Descricao" value={description} onChange={(e) => setDescription(e.target.value)} multiline minRows={3} fullWidth />
      <FormControlLabel
        control={<Switch checked={isRecurring} onChange={(e) => setIsRecurring(e.target.checked)} />}
        label="Recorrente"
      />
      {isRecurring ? (
        <>
          <FormControl fullWidth>
            <InputLabel id="requirements-period-type-label">Periodo</InputLabel>
            <Select
              labelId="requirements-period-type-label"
              value={periodType}
              label="Periodo"
              onChange={(e) => setPeriodType(String(e.target.value))}
            >
              <MenuItem value="week">week</MenuItem>
              <MenuItem value="month">month</MenuItem>
              <MenuItem value="year">year</MenuItem>
              <MenuItem value="contract_term">contract_term</MenuItem>
              <MenuItem value="custom">custom</MenuItem>
            </Select>
          </FormControl>
          <TextField label="Regra do periodo" value={periodRule} onChange={(e) => setPeriodRule(e.target.value)} fullWidth />
          <TextField label="Ocorrencias esperadas" value={expectedOccurrences} onChange={(e) => setExpectedOccurrences(e.target.value)} fullWidth />
          <TextField label="Inicio" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
          <TextField label="Fim" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
        </>
      ) : null}
      <FormControl fullWidth>
        <InputLabel id="requirements-responsibility-label">Responsabilidade</InputLabel>
        <Select
          labelId="requirements-responsibility-label"
          value={responsibilityType}
          label="Responsabilidade"
          onChange={(e) => setResponsibilityType(String(e.target.value))}
        >
          <MenuItem value="individual">individual</MenuItem>
          <MenuItem value="collective">collective</MenuItem>
        </Select>
      </FormControl>
      <FormControl fullWidth>
        <InputLabel id="requirements-status-label">Status</InputLabel>
        <Select
          labelId="requirements-status-label"
          value={status}
          label="Status"
          onChange={(e) => setStatus(String(e.target.value))}
        >
          <MenuItem value="planned">planned</MenuItem>
          <MenuItem value="in_progress">in_progress</MenuItem>
          <MenuItem value="fulfilled">fulfilled</MenuItem>
          <MenuItem value="expired">expired</MenuItem>
        </Select>
      </FormControl>
      <Box>
        <Button variant="contained" disabled={selectedContractId == null} onClick={() => void handleCreate()}>
          Criar contrapartida
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Tipo</TableCell>
              <TableCell>Clausula</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Ocorrencias</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {requirements.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography color="text.secondary">Nenhuma contrapartida cadastrada.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              requirements.map((requirement) => (
                <TableRow key={requirement.id}>
                  <TableCell>{requirement.requirement_type}</TableCell>
                  <TableCell>{clauseMap[requirement.clause_id] || requirement.clause_id}</TableCell>
                  <TableCell>{requirement.status}</TableCell>
                  <TableCell align="center">{requirement.occurrences_count}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={() => void handleDelete(requirement.id)}>
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
