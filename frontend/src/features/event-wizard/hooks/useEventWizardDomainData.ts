import { useCallback, useEffect, useState } from "react";
import { Agencia, listAgencias } from "../../../services/agencias";
import {
  DivisaoDemandante,
  Diretoria,
  listDivisoesDemandantes,
  listDiretorias,
  listSubtiposEvento,
  listTags,
  listTerritorios,
  listTiposEvento,
  SubtipoEvento,
  Tag,
  Territorio,
  TipoEvento,
} from "../../../services/eventos";

type EstadosCidadesData = {
  estados: Array<{
    sigla: string;
    nome: string;
    cidades: string[];
  }>;
};

let cachedCidadesPorUf: Record<string, string[]> | null = null;

async function getCidadesPorUf(): Promise<Record<string, string[]>> {
  if (cachedCidadesPorUf) return cachedCidadesPorUf;
  const mod = await import("../../../data/estados-cidades.json");
  const data = ((mod as { default?: unknown }).default ?? mod) as EstadosCidadesData;
  cachedCidadesPorUf = Object.fromEntries(
    data.estados.map((estado) => [
      String(estado.sigla).toUpperCase(),
      Array.isArray(estado.cidades) ? estado.cidades : [],
    ]),
  );
  return cachedCidadesPorUf;
}

/**
 * Loads and keeps domain/reference data used across event wizard steps.
 * @param params Hook dependencies for auth, selected step values and default agency behavior.
 * @returns Domain lists, loading/error flags and refresh handlers for wizard UI.
 */
export function useEventWizardDomainData(params: {
  token: string | null;
  canPickAgencia: boolean;
  selectedTipoId: number | null;
  estado: string;
  userAgenciaId?: number | null;
  onApplyUserAgencia?: (agenciaId: string) => void;
}) {
  const { token, canPickAgencia, selectedTipoId, estado, userAgenciaId, onApplyUserAgencia } = params;

  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [divisoesDemandantes, setDivisoesDemandantes] = useState<DivisaoDemandante[]>([]);
  const [tipos, setTipos] = useState<TipoEvento[]>([]);
  const [subtipos, setSubtipos] = useState<SubtipoEvento[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [territorios, setTerritorios] = useState<Territorio[]>([]);
  const [cidades, setCidades] = useState<string[]>([]);

  const [loadingDomains, setLoadingDomains] = useState(false);
  const [loadingCidades, setLoadingCidades] = useState(false);
  const [loadingSubtipos, setLoadingSubtipos] = useState(false);
  const [domainError, setDomainError] = useState<string | null>(null);

  const reloadDomains = useCallback(async () => {
    if (!token) return;
    setLoadingDomains(true);
    setDomainError(null);

    try {
      const [agenciasResult, diretoriasResult, divisoesResult, tiposResult, tagsResult, territoriosResult] =
        await Promise.all([
          canPickAgencia ? listAgencias({ limit: 200 }) : Promise.resolve([] as Agencia[]),
          listDiretorias(token),
          listDivisoesDemandantes(token),
          listTiposEvento(token),
          listTags(token),
          listTerritorios(token),
        ]);

      setAgencias(canPickAgencia ? agenciasResult : []);
      setDiretorias(diretoriasResult);
      setDivisoesDemandantes(divisoesResult);
      setTipos(tiposResult);
      setTags(tagsResult);
      setTerritorios(territoriosResult);

      if (userAgenciaId && onApplyUserAgencia) {
        onApplyUserAgencia(String(userAgenciaId));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro ao carregar dominios";
      setDomainError(message);
    } finally {
      setLoadingDomains(false);
    }
  }, [token, canPickAgencia, userAgenciaId, onApplyUserAgencia]);

  useEffect(() => {
    reloadDomains();
  }, [reloadDomains]);

  useEffect(() => {
    const uf = String(estado || "").trim().toUpperCase();
    if (!uf) {
      setCidades([]);
      return;
    }

    let cancelled = false;
    setLoadingCidades(true);

    getCidadesPorUf()
      .then((cidadesPorUf) => {
        if (cancelled) return;
        setCidades(cidadesPorUf[uf] ?? []);
      })
      .catch(() => {
        if (cancelled) return;
        setCidades([]);
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingCidades(false);
      });

    return () => {
      cancelled = true;
    };
  }, [estado]);

  useEffect(() => {
    if (!token) return;
    if (!selectedTipoId) {
      setSubtipos([]);
      return;
    }

    let cancelled = false;
    setLoadingSubtipos(true);

    listSubtiposEvento(token, { tipo_id: selectedTipoId })
      .then((items) => {
        if (cancelled) return;
        setSubtipos(items);
      })
      .catch(() => {
        if (cancelled) return;
        setSubtipos([]);
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingSubtipos(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, selectedTipoId]);

  return {
    agencias,
    diretorias,
    divisoesDemandantes,
    tipos,
    subtipos,
    tags,
    territorios,
    cidades,
    loadingDomains,
    loadingCidades,
    loadingSubtipos,
    domainError,
    setDomainError,
    reloadDomains,
  };
}
