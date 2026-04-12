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
  createDeliveryEvidence,
  createOccurrenceDelivery,
  deleteOccurrenceDelivery,
  listDeliveryEvidences,
  listOccurrenceDeliveries,
} from "../../../services/sponsorship";
import { toApiErrorMessage } from "../../../services/http";
import type { DeliveryEvidenceRead, DeliveryRead, RequirementOccurrenceRead } from "../../../types/sponsorship";

type GroupDeliveriesPanelProps = {
  token: string | null;
  occurrences: RequirementOccurrenceRead[];
  selectedOccurrenceId: number | null;
  onSelectOccurrence: (occurrenceId: number | null) => void;
  onError: (message: string) => void;
};

function normalizeSelectedId(current: number | null, nextIds: number[]) {
  if (nextIds.length === 0) return null;
  if (current != null && nextIds.includes(current)) return current;
  return nextIds[0];
}

export default function GroupDeliveriesPanel({
  token,
  occurrences,
  selectedOccurrenceId,
  onSelectOccurrence,
  onError,
}: GroupDeliveriesPanelProps) {
  const [deliveries, setDeliveries] = useState<DeliveryRead[]>([]);
  const [evidences, setEvidences] = useState<DeliveryEvidenceRead[]>([]);
  const [selectedDeliveryId, setSelectedDeliveryId] = useState<number | null>(null);
  const [description, setDescription] = useState("");
  const [observations, setObservations] = useState("");
  const [evidenceType, setEvidenceType] = useState("link");
  const [url, setUrl] = useState("");
  const [evidenceDescription, setEvidenceDescription] = useState("");
  const [platform, setPlatform] = useState("");
  const [externalId, setExternalId] = useState("");
  const [postedAt, setPostedAt] = useState("");

  const loadDeliveries = useCallback(async () => {
    if (!token || selectedOccurrenceId == null) {
      setDeliveries([]);
      return;
    }
    try {
      const data = await listOccurrenceDeliveries(token, selectedOccurrenceId);
      setDeliveries(data);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar as entregas."));
    }
  }, [onError, selectedOccurrenceId, token]);

  const loadEvidences = useCallback(async () => {
    if (!token || selectedDeliveryId == null) {
      setEvidences([]);
      return;
    }
    try {
      const data = await listDeliveryEvidences(token, selectedDeliveryId);
      setEvidences(data);
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel carregar as evidencias."));
    }
  }, [onError, selectedDeliveryId, token]);

  useEffect(() => {
    void loadDeliveries();
  }, [loadDeliveries]);

  useEffect(() => {
    setSelectedDeliveryId((current) =>
      normalizeSelectedId(current, deliveries.map((delivery) => delivery.id)),
    );
  }, [deliveries]);

  useEffect(() => {
    void loadEvidences();
  }, [loadEvidences]);

  const handleCreateDelivery = async () => {
    if (!token || selectedOccurrenceId == null) return;
    if (!description.trim()) {
      onError("Informe a descricao da entrega.");
      return;
    }
    try {
      await createOccurrenceDelivery(token, selectedOccurrenceId, {
        description: description.trim(),
        observations: observations.trim() || null,
      });
      setDescription("");
      setObservations("");
      await loadDeliveries();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel registrar a entrega."));
    }
  };

  const handleDeleteDelivery = async (deliveryId: number) => {
    if (!token || selectedOccurrenceId == null) return;
    try {
      await deleteOccurrenceDelivery(token, selectedOccurrenceId, deliveryId);
      await loadDeliveries();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel remover a entrega."));
    }
  };

  const handleCreateEvidence = async () => {
    if (!token || selectedDeliveryId == null) return;
    try {
      await createDeliveryEvidence(token, selectedDeliveryId, {
        evidence_type: evidenceType as any,
        url: url.trim() || null,
        description: evidenceDescription.trim() || null,
        platform: platform.trim() || null,
        external_id: externalId.trim() || null,
        posted_at: postedAt || null,
      });
      setEvidenceType("link");
      setUrl("");
      setEvidenceDescription("");
      setPlatform("");
      setExternalId("");
      setPostedAt("");
      await loadEvidences();
    } catch (err) {
      onError(toApiErrorMessage(err, "Nao foi possivel registrar a evidencia."));
    }
  };

  return (
    <Stack spacing={2}>
      <FormControl fullWidth>
        <InputLabel id="deliveries-occurrence-label">Ocorrencia</InputLabel>
        <Select
          labelId="deliveries-occurrence-label"
          value={selectedOccurrenceId == null ? "" : String(selectedOccurrenceId)}
          label="Ocorrencia"
          onChange={(e) => onSelectOccurrence(e.target.value ? Number(e.target.value) : null)}
        >
          {occurrences.map((occurrence) => (
            <MenuItem key={occurrence.id} value={String(occurrence.id)}>
              {occurrence.period_label || `Ocorrencia #${occurrence.id}`}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField label="Descricao da entrega" value={description} onChange={(e) => setDescription(e.target.value)} multiline minRows={2} fullWidth />
      <TextField label="Observacoes" value={observations} onChange={(e) => setObservations(e.target.value)} multiline minRows={2} fullWidth />
      <Box>
        <Button variant="contained" disabled={selectedOccurrenceId == null} onClick={() => void handleCreateDelivery()}>
          Registrar entrega
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Descricao</TableCell>
              <TableCell>Observacoes</TableCell>
              <TableCell align="right">Acoes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {deliveries.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography color="text.secondary">Nenhuma entrega registrada.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              deliveries.map((delivery) => (
                <TableRow
                  key={delivery.id}
                  selected={selectedDeliveryId === delivery.id}
                  hover
                  onClick={() => setSelectedDeliveryId(delivery.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell>{delivery.description}</TableCell>
                  <TableCell>{delivery.observations || "-"}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" size="small" onClick={(event) => {
                      event.stopPropagation();
                      void handleDeleteDelivery(delivery.id);
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
        Evidencias da entrega selecionada
      </Typography>
      <FormControl fullWidth>
        <InputLabel id="deliveries-evidence-type-label">Tipo</InputLabel>
        <Select
          labelId="deliveries-evidence-type-label"
          value={evidenceType}
          label="Tipo"
          onChange={(e) => setEvidenceType(String(e.target.value))}
        >
          <MenuItem value="link">link</MenuItem>
          <MenuItem value="file">file</MenuItem>
          <MenuItem value="text">text</MenuItem>
          <MenuItem value="social_post">social_post</MenuItem>
          <MenuItem value="image">image</MenuItem>
          <MenuItem value="other">other</MenuItem>
        </Select>
      </FormControl>
      <TextField label="URL" value={url} onChange={(e) => setUrl(e.target.value)} fullWidth />
      <TextField label="Descricao" value={evidenceDescription} onChange={(e) => setEvidenceDescription(e.target.value)} fullWidth />
      <TextField label="Plataforma" value={platform} onChange={(e) => setPlatform(e.target.value)} fullWidth />
      <TextField label="ID externo" value={externalId} onChange={(e) => setExternalId(e.target.value)} fullWidth />
      <TextField label="Publicado em" type="datetime-local" value={postedAt} onChange={(e) => setPostedAt(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
      <Box>
        <Button variant="outlined" disabled={selectedDeliveryId == null} onClick={() => void handleCreateEvidence()}>
          Registrar evidencia
        </Button>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Tipo</TableCell>
              <TableCell>Descricao</TableCell>
              <TableCell>URL</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {evidences.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography color="text.secondary">Nenhuma evidencia registrada.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              evidences.map((evidence) => (
                <TableRow key={evidence.id}>
                  <TableCell>{evidence.evidence_type}</TableCell>
                  <TableCell>{evidence.description || "-"}</TableCell>
                  <TableCell>{evidence.url || "-"}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
