import { useMemo, useState } from "react";
import {
  Box,
  Button,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Paper,
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

import { createGroupMember, deleteGroupMember } from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type {
  GroupMemberRead,
  SponsoredInstitutionRead,
  SponsoredPersonRead,
} from "../../../types/sponsorship";

type GroupMembersPanelProps = {
  token: string | null;
  groupId: number;
  members: GroupMemberRead[];
  persons: SponsoredPersonRead[];
  institutions: SponsoredInstitutionRead[];
  onChanged: () => void;
  onError: (message: string) => void;
};

export default function GroupMembersPanel({
  token,
  groupId,
  members,
  persons,
  institutions,
  onChanged,
  onError,
}: GroupMembersPanelProps) {
  const [ownerType, setOwnerType] = useState<"person" | "institution">("person");
  const [ownerId, setOwnerId] = useState("");
  const [roleInGroup, setRoleInGroup] = useState("");

  const ownerOptions = ownerType === "person" ? persons : institutions;
  const memberLabels = useMemo(
    () =>
      Object.fromEntries([
        ...persons.map((person) => [person.id, person.full_name]),
        ...institutions.map((institution) => [institution.id, institution.name]),
      ]),
    [institutions, persons],
  );

  const handleCreate = async () => {
    if (!token) return;
    if (!ownerId) {
      onError("Selecione uma pessoa ou instituicao.");
      return;
    }
    try {
      await createGroupMember(token, groupId, {
        person_id: ownerType === "person" ? Number(ownerId) : null,
        institution_id: ownerType === "institution" ? Number(ownerId) : null,
        role_in_group: roleInGroup.trim() || null,
      });
      setOwnerId("");
      setRoleInGroup("");
      onChanged();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel adicionar o membro."));
    }
  };

  const handleDelete = async (memberId: number) => {
    if (!token) return;
    try {
      await deleteGroupMember(token, groupId, memberId);
      onChanged();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover o membro."));
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1" fontWeight={800}>
        Adicionar membro
      </Typography>
      <FormControl fullWidth>
        <InputLabel id="group-member-type-label">Tipo</InputLabel>
        <Select
          labelId="group-member-type-label"
          value={ownerType}
          label="Tipo"
          onChange={(e) => {
            setOwnerType(e.target.value as "person" | "institution");
            setOwnerId("");
          }}
        >
          <MenuItem value="person">Pessoa</MenuItem>
          <MenuItem value="institution">Instituicao</MenuItem>
        </Select>
      </FormControl>
      <FormControl fullWidth>
        <InputLabel id="group-member-owner-label">
          {ownerType === "person" ? "Pessoa" : "Instituicao"}
        </InputLabel>
        <Select
          labelId="group-member-owner-label"
          value={ownerId}
          label={ownerType === "person" ? "Pessoa" : "Instituicao"}
          onChange={(e) => setOwnerId(String(e.target.value))}
        >
          {ownerOptions.map((owner) => (
            <MenuItem key={owner.id} value={String(owner.id)}>
              {"full_name" in owner ? owner.full_name : owner.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField label="Papel no grupo" value={roleInGroup} onChange={(e) => setRoleInGroup(e.target.value)} fullWidth />
      <Box>
        <Button variant="contained" onClick={() => void handleCreate()}>
          Adicionar membro
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Tipo</TableCell>
              <TableCell>Referencia</TableCell>
              <TableCell>Papel no grupo</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {members.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary">Nenhum membro cadastrado.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              members.map((member) => (
                <TableRow key={member.id}>
                  <TableCell>{member.person_id != null ? "Pessoa" : "Instituicao"}</TableCell>
                  <TableCell>
                    {member.person_id != null
                      ? memberLabels[member.person_id]
                      : member.institution_id != null
                        ? memberLabels[member.institution_id]
                        : "-"}
                  </TableCell>
                  <TableCell>{member.role_in_group || "-"}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={() => void handleDelete(member.id)}>
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
