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
  createOccurrenceResponsible,
  createRequirementOccurrence,
  deleteOccurrenceResponsible,
  deleteRequirementOccurrence,
  listOccurrenceResponsibles,
  listRequirementOccurrences,
} from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type {
  GroupMemberRead,
  OccurrenceResponsibleRead,
  RequirementOccurrenceRead,
  SponsoredInstitutionRead,
  SponsoredPersonRead,
  CounterpartRequirementRead,
} from "../../../types/sponsorship";

type GroupOccurrencesPanelProps = {
  token: string | null;
  members: GroupMemberRead[];
  persons: SponsoredPersonRead[];
  institutions: SponsoredInstitutionRead[];
  requirements: CounterpartRequirementRead[];
  selectedRequirementId: number | null;
  onSelectRequirement: (requirementId: number | null) => void;
  selectedOccurrenceId: number | null;
  onSelectOccurrence: (occurrenceId: number | null) => void;
  onOccurrencesChange: (occurrences: RequirementOccurrenceRead[]) => void;
  onError: (message: string) => void;
};

export default function GroupOccurrencesPanel({
  token,
  members,
  persons,
  institutions,
  requirements,
  selectedRequirementId,
  onSelectRequirement,
  selectedOccurrenceId,
  onSelectOccurrence,
  onOccurrencesChange,
  onError,
}: GroupOccurrencesPanelProps) {
  const [occurrences, setOccurrences] = useState<RequirementOccurrenceRead[]>([]);
  const [responsibles, setResponsibles] = useState<OccurrenceResponsibleRead[]>([]);
  const [periodLabel, setPeriodLabel] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [responsibilityType, setResponsibilityType] = useState("individual");
  const [status, setStatus] = useState("pending");
  const [internalNotes, setInternalNotes] = useState("");
  const [memberId, setMemberId] = useState("");
  const [roleDescription, setRoleDescription] = useState("");
  const [isPrimary, setIsPrimary] = useState(true);

  const memberLabels = useMemo(
    () =>
      Object.fromEntries(
        members.map((member) => [
          member.id,
          member.person_id != null
            ? persons.find((person) => person.id === member.person_id)?.full_name || `Pessoa #${member.person_id}`
            : institutions.find((institution) => institution.id === member.institution_id)?.name ||
              `Instituicao #${member.institution_id}`,
        ]),
      ),
    [institutions, members, persons],
  );

  const loadOccurrences = useCallback(async () => {
    if (!token || selectedRequirementId == null) {
      setOccurrences([]);
      onOccurrencesChange([]);
      return;
    }
    try {
      const data = await listRequirementOccurrences(token, selectedRequirementId);
      setOccurrences(data);
      onOccurrencesChange(data);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar as ocorrencias."));
    }
  }, [onError, onOccurrencesChange, selectedRequirementId, token]);

  const loadResponsibles = useCallback(async () => {
    if (!token || selectedOccurrenceId == null) {
      setResponsibles([]);
      return;
    }
    try {
      const data = await listOccurrenceResponsibles(token, selectedOccurrenceId);
      setResponsibles(data);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar os responsaveis."));
    }
  }, [onError, selectedOccurrenceId, token]);

  useEffect(() => {
    void loadOccurrences();
  }, [loadOccurrences]);

  useEffect(() => {
    void loadResponsibles();
  }, [loadResponsibles]);

  const handleCreateOccurrence = async () => {
    if (!token || selectedRequirementId == null) return;
    try {
      await createRequirementOccurrence(token, selectedRequirementId, {
        period_label: periodLabel.trim() || null,
        due_date: dueDate || null,
        responsibility_type: responsibilityType as any,
        status: status as any,
        internal_notes: internalNotes.trim() || null,
      });
      setPeriodLabel("");
      setDueDate("");
      setResponsibilityType("individual");
      setStatus("pending");
      setInternalNotes("");
      await loadOccurrences();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel criar a ocorrencia."));
    }
  };

  const handleDeleteOccurrence = async (occurrenceId: number) => {
    if (!token || selectedRequirementId == null) return;
    try {
      await deleteRequirementOccurrence(token, selectedRequirementId, occurrenceId);
      await loadOccurrences();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover a ocorrencia."));
    }
  };

  const handleCreateResponsible = async () => {
    if (!token || selectedOccurrenceId == null) return;
    if (!memberId) {
      onError("Selecione um membro do grupo.");
      return;
    }
    try {
      await createOccurrenceResponsible(token, selectedOccurrenceId, {
        member_id: Number(memberId),
        is_primary: isPrimary,
        role_description: roleDescription.trim() || null,
      });
      setMemberId("");
      setRoleDescription("");
      setIsPrimary(true);
      await loadResponsibles();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel vincular o responsavel."));
    }
  };

  const handleDeleteResponsible = async (responsibleId: number) => {
    if (!token || selectedOccurrenceId == null) return;
    try {
      await deleteOccurrenceResponsible(token, selectedOccurrenceId, responsibleId);
      await loadResponsibles();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover o responsavel."));
    }
  };

  return (
    <Stack spacing={2}>
      <FormControl fullWidth>
        <InputLabel id="occurrence-requirement-label">Contrapartida</InputLabel>
        <Select
          labelId="occurrence-requirement-label"
          value={selectedRequirementId == null ? "" : String(selectedRequirementId)}
          label="Contrapartida"
          onChange={(e) => onSelectRequirement(e.target.value ? Number(e.target.value) : null)}
        >
          {requirements.map((requirement) => (
            <MenuItem key={requirement.id} value={String(requirement.id)}>
              {requirement.requirement_type}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField label="Periodo" value={periodLabel} onChange={(e) => setPeriodLabel(e.target.value)} fullWidth />
      <TextField label="Prazo" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
      <FormControl fullWidth>
        <InputLabel id="occurrence-responsibility-type-label">Tipo de responsabilidade</InputLabel>
        <Select
          labelId="occurrence-responsibility-type-label"
          value={responsibilityType}
          label="Tipo de responsabilidade"
          onChange={(e) => setResponsibilityType(String(e.target.value))}
        >
          <MenuItem value="individual">individual</MenuItem>
          <MenuItem value="collective">collective</MenuItem>
        </Select>
      </FormControl>
      <FormControl fullWidth>
        <InputLabel id="occurrence-status-panel-label">Status</InputLabel>
        <Select
          labelId="occurrence-status-panel-label"
          value={status}
          label="Status"
          onChange={(e) => setStatus(String(e.target.value))}
        >
          <MenuItem value="pending">pending</MenuItem>
          <MenuItem value="in_review">in_review</MenuItem>
          <MenuItem value="delivered">delivered</MenuItem>
          <MenuItem value="validated">validated</MenuItem>
          <MenuItem value="rejected">rejected</MenuItem>
        </Select>
      </FormControl>
      <TextField label="Notas internas" value={internalNotes} onChange={(e) => setInternalNotes(e.target.value)} multiline minRows={2} fullWidth />
      <Box>
        <Button variant="contained" disabled={selectedRequirementId == null} onClick={() => void handleCreateOccurrence()}>
          Criar ocorrencia
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Periodo</TableCell>
              <TableCell>Prazo</TableCell>
              <TableCell>Responsabilidade</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {occurrences.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography color="text.secondary">Nenhuma ocorrencia cadastrada.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              occurrences.map((occurrence) => (
                <TableRow
                  key={occurrence.id}
                  selected={selectedOccurrenceId === occurrence.id}
                  hover
                  onClick={() => onSelectOccurrence(occurrence.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell>{occurrence.period_label || "-"}</TableCell>
                  <TableCell>{occurrence.due_date || "-"}</TableCell>
                  <TableCell>{occurrence.responsibility_type}</TableCell>
                  <TableCell>{occurrence.status}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={(event) => {
                      event.stopPropagation();
                      void handleDeleteOccurrence(occurrence.id);
                    }}>
                      <DeleteOutlineIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="subtitle1" fontWeight={800}>
        Responsaveis da ocorrencia selecionada
      </Typography>
      <FormControl fullWidth>
        <InputLabel id="occurrence-member-label">Membro</InputLabel>
        <Select
          labelId="occurrence-member-label"
          value={memberId}
          label="Membro"
          onChange={(e) => setMemberId(String(e.target.value))}
        >
          {members.map((member) => (
            <MenuItem key={member.id} value={String(member.id)}>
              {memberLabels[member.id]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField label="Papel" value={roleDescription} onChange={(e) => setRoleDescription(e.target.value)} fullWidth />
      <FormControlLabel
        control={<Switch checked={isPrimary} onChange={(e) => setIsPrimary(e.target.checked)} />}
        label="Responsavel principal"
      />
      <Box>
        <Button variant="outlined" disabled={selectedOccurrenceId == null} onClick={() => void handleCreateResponsible()}>
          Vincular responsavel
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Membro</TableCell>
              <TableCell>Papel</TableCell>
              <TableCell align="center">Principal</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {responsibles.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary">Nenhum responsavel vinculado.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              responsibles.map((responsible) => (
                <TableRow key={responsible.id}>
                  <TableCell>{memberLabels[responsible.member_id] || `Membro #${responsible.member_id}`}</TableCell>
                  <TableCell>{responsible.role_description || "-"}</TableCell>
                  <TableCell align="center">{responsible.is_primary ? "Sim" : "Nao"}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={() => void handleDeleteResponsible(responsible.id)}>
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
