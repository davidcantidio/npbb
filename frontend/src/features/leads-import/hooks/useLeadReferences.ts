import { useEffect, useMemo, useState } from "react";
import {
  listReferenciaCidades,
  listReferenciaEstados,
  listReferenciaEventos,
  listReferenciaGeneros,
  LeadImportPreview,
} from "../../../services/leads_import";

/**
 * Loads and normalizes reference data used by assisted lead mapping.
 * @param token Auth token used by reference endpoints.
 * @param preview Current preview payload; controls whether references should be loaded.
 * @returns Canonical option lists consumed by mapping selectors.
 */
export function useLeadReferences(token: string | null, preview: LeadImportPreview | null) {
  const [eventosRef, setEventosRef] = useState<Array<{ id: number; nome: string }>>([]);
  const [cidadesRef, setCidadesRef] = useState<string[]>([]);
  const [estadosRef, setEstadosRef] = useState<string[]>([]);
  const [generosRef, setGenerosRef] = useState<string[]>([]);

  useEffect(() => {
    if (!token || !preview) return;

    Promise.all([
      listReferenciaEventos(token),
      listReferenciaCidades(token),
      listReferenciaEstados(token),
      listReferenciaGeneros(token),
    ])
      .then(([eventos, cidades, estados, generos]) => {
        setEventosRef(eventos);
        setCidadesRef(cidades);
        setEstadosRef(estados);
        setGenerosRef(generos);
      })
      .catch(() => {
        // references are best-effort helpers
      });
  }, [token, preview]);

  const referenceOptions = useMemo(() => {
    return {
      evento_nome: eventosRef.map((evento) => ({ value: String(evento.id), label: evento.nome })),
      cidade: cidadesRef.map((cidade) => ({ value: cidade, label: cidade })),
      estado: estadosRef.map((estado) => ({ value: estado, label: estado })),
      genero: generosRef.map((genero) => ({ value: genero, label: genero })),
    };
  }, [cidadesRef, estadosRef, eventosRef, generosRef]);

  return {
    referenceOptions,
  };
}
