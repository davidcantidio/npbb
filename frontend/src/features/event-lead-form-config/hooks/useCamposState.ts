import { useCallback, useMemo, useState } from "react";
import type { PreviewEventoLandingPayload } from "../../../services/landing_public";

export type FormularioCampoInput = {
  nome_campo: string;
  obrigatorio: boolean;
  ordem?: number;
};

function normalizeCampoNome(nome: string) {
  return String(nome || "")
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ");
}

const CAMPOS_DEFAULTS = ["CPF", "Nome", "Sobrenome", "Data de nascimento"] as const;
const CAMPOS_SEMPRE_OBRIGATORIOS = new Set([normalizeCampoNome("CPF")]);

function isCampoSempreObrigatorioNome(nome: string) {
  return CAMPOS_SEMPRE_OBRIGATORIOS.has(normalizeCampoNome(nome));
}

function buildUniqueCampos(camposPossiveis: string[]) {
  const seen = new Set<string>();
  const items: string[] = [];
  for (const nome of camposPossiveis) {
    const normalized = String(nome || "").trim();
    if (!normalized) continue;

    const normalizedKey = normalizeCampoNome(normalized);
    if (seen.has(normalizedKey)) continue;

    seen.add(normalizedKey);
    items.push(normalized);
  }
  return items;
}

function createCatalogLookup(camposPossiveis: string[]) {
  return new Map(camposPossiveis.map((nome) => [normalizeCampoNome(nome), nome]));
}

function getDefaultCampos(catalogLookup: Map<string, string>) {
  return CAMPOS_DEFAULTS.map((nome) => catalogLookup.get(normalizeCampoNome(nome))).filter(
    (nome): nome is string => Boolean(nome),
  );
}

function sortCamposConfigurados(campos: FormularioCampoInput[]) {
  return [...campos].sort((left, right) => {
    const leftOrder = Number.isFinite(left?.ordem) ? Number(left.ordem) : Number.MAX_SAFE_INTEGER;
    const rightOrder = Number.isFinite(right?.ordem)
      ? Number(right.ordem)
      : Number.MAX_SAFE_INTEGER;

    if (leftOrder !== rightOrder) {
      return leftOrder - rightOrder;
    }

    return String(left?.nome_campo || "").localeCompare(String(right?.nome_campo || ""));
  });
}

function moveCampoNaLista(campos: string[], activeNome: string, overNome: string) {
  const activeIndex = campos.findIndex((item) => item === activeNome);
  const overIndex = campos.findIndex((item) => item === overNome);
  if (activeIndex === -1 || overIndex === -1 || activeIndex === overIndex) return campos;

  const next = [...campos];
  const [moved] = next.splice(activeIndex, 1);
  next.splice(overIndex, 0, moved);
  return next;
}

export function useCamposState(camposPossiveis: string[]) {
  const [camposAtivos, setCamposAtivos] = useState<Set<string>>(() => new Set());
  const [camposObrigatorios, setCamposObrigatorios] = useState<Record<string, boolean>>(
    () => ({}),
  );
  const [camposOrdemAtivos, setCamposOrdemAtivos] = useState<string[]>([]);

  const camposPossiveisUniq = useMemo(() => {
    return buildUniqueCampos(camposPossiveis);
  }, [camposPossiveis]);

  const camposAtivosOrdenados = useMemo(() => {
    const ativosByKey = new Map(
      [...camposAtivos].map((nome) => [normalizeCampoNome(nome), nome]),
    );
    const usados = new Set<string>();
    const ordered: string[] = [];

    for (const nome of camposOrdemAtivos) {
      const key = normalizeCampoNome(nome);
      const canonical = ativosByKey.get(key);
      if (!canonical || usados.has(key)) continue;

      usados.add(key);
      ordered.push(canonical);
    }

    for (const nome of camposPossiveisUniq) {
      const key = normalizeCampoNome(nome);
      const canonical = ativosByKey.get(key);
      if (!canonical || usados.has(key)) continue;

      usados.add(key);
      ordered.push(canonical);
    }

    for (const nome of camposAtivos) {
      const key = normalizeCampoNome(nome);
      if (usados.has(key)) continue;

      usados.add(key);
      ordered.push(nome);
    }

    return ordered;
  }, [camposAtivos, camposOrdemAtivos, camposPossiveisUniq]);

  const camposDisponiveis = useMemo(
    () => camposPossiveisUniq.filter((nome) => !camposAtivos.has(nome)),
    [camposAtivos, camposPossiveisUniq],
  );

  const camposPayload = useMemo(() => {
    return camposAtivosOrdenados.map((nome, index) => ({
      nome_campo: nome,
      obrigatorio: isCampoSempreObrigatorioNome(nome) ? true : (camposObrigatorios[nome] ?? true),
      ordem: index,
    }));
  }, [camposAtivosOrdenados, camposObrigatorios]);

  const toggleCampo = useCallback((nome: string) => {
    setCamposAtivos((prev) => {
      const next = new Set(prev);
      const wasActive = next.has(nome);
      if (wasActive) {
        if (isCampoSempreObrigatorioNome(nome)) return prev;

        next.delete(nome);
        setCamposOrdemAtivos((prevOrdem) => prevOrdem.filter((item) => item !== nome));
        return next;
      }

      next.add(nome);
      setCamposOrdemAtivos((prevOrdem) =>
        prevOrdem.includes(nome) ? prevOrdem : [...prevOrdem, nome],
      );

      setCamposObrigatorios((prevObrigatorios) => {
        if (Object.prototype.hasOwnProperty.call(prevObrigatorios, nome)) return prevObrigatorios;
        return { ...prevObrigatorios, [nome]: true };
      });

      return next;
    });
  }, []);

  const setCampoObrigatorio = useCallback((nome: string, obrigatorio: boolean) => {
    if (isCampoSempreObrigatorioNome(nome) && !obrigatorio) return;
    setCamposObrigatorios((prev) => ({ ...prev, [nome]: obrigatorio }));
  }, []);

  const reorderCampoAtivo = useCallback((activeNome: string, overNome: string) => {
    setCamposOrdemAtivos((prev) => moveCampoNaLista(prev, activeNome, overNome));
  }, []);

  const syncFromConfig = useCallback(
    (campos: FormularioCampoInput[] | null | undefined, catalog?: string[]) => {
      const catalogSource = buildUniqueCampos(catalog ?? camposPossiveis);
      const catalogLookup = createCatalogLookup(catalogSource);
      const nextAtivos = new Set<string>();
      const nextObrigatorios: Record<string, boolean> = {};
      const nextOrdem: string[] = [];

      const ensureCampoAtivo = (nome: string, obrigatorio = true) => {
        if (nextAtivos.has(nome)) return;
        nextAtivos.add(nome);
        nextObrigatorios[nome] = isCampoSempreObrigatorioNome(nome) ? true : obrigatorio;
        nextOrdem.push(nome);
      };

      const camposConfigurados = sortCamposConfigurados(campos ?? []);
      if (camposConfigurados.length) {
        for (const campo of camposConfigurados) {
          const normalized = String(campo?.nome_campo || "").trim();
          if (!normalized) continue;

          const canonical = catalogLookup.get(normalizeCampoNome(normalized)) ?? normalized;
          ensureCampoAtivo(canonical, Boolean(campo?.obrigatorio));
        }
      } else {
        getDefaultCampos(catalogLookup).forEach((nome) => ensureCampoAtivo(nome));
      }

      const cpfCanonical = catalogLookup.get(normalizeCampoNome("CPF"));
      if (cpfCanonical && !nextAtivos.has(cpfCanonical)) {
        nextAtivos.add(cpfCanonical);
        nextObrigatorios[cpfCanonical] = true;
        nextOrdem.unshift(cpfCanonical);
      }

      setCamposAtivos(nextAtivos);
      setCamposObrigatorios(nextObrigatorios);
      setCamposOrdemAtivos(nextOrdem);
    },
    [camposPossiveis],
  );

  return {
    camposAtivos,
    camposAtivosOrdenados,
    camposDisponiveis,
    camposObrigatorios,
    camposPossiveisUniq,
    camposPayload,
    isCampoSempreObrigatorio: isCampoSempreObrigatorioNome,
    toggleCampo,
    setCampoObrigatorio,
    reorderCampoAtivo,
    setCamposAtivos,
    setCamposObrigatorios,
    setCamposOrdemAtivos,
    syncFromConfig,
  };
}
