import { useCallback, useMemo, useState } from "react";
import type { PreviewEventoLandingPayload } from "../../../services/landing_public";

export type FormularioCampoInput = {
  nome_campo: string;
  obrigatorio: boolean;
  ordem?: number;
};

export function useCamposState(camposPossiveis: string[]) {
  const [camposAtivos, setCamposAtivos] = useState<Set<string>>(() => new Set());
  const [camposObrigatorios, setCamposObrigatorios] = useState<Record<string, boolean>>(
    () => ({}),
  );

  const camposPossiveisUniq = useMemo(() => {
    const seen = new Set<string>();
    const items: string[] = [];
    for (const nome of camposPossiveis) {
      const normalized = String(nome || "").trim();
      if (!normalized) continue;
      if (seen.has(normalized.toLowerCase())) continue;
      seen.add(normalized.toLowerCase());
      items.push(normalized);
    }
    return items;
  }, [camposPossiveis]);

  const camposPayload = useMemo(() => {
    const ordemByLower = new Map(
      camposPossiveisUniq.map((nome, index) => [nome.toLowerCase(), index]),
    );
    const payload: NonNullable<PreviewEventoLandingPayload["campos"]> = camposPossiveisUniq
      .map((nome, index) => {
        if (!camposAtivos.has(nome)) return null;
        return {
          nome_campo: nome,
          obrigatorio: camposObrigatorios[nome] ?? true,
          ordem: index,
        };
      })
      .filter(
        (value): value is NonNullable<PreviewEventoLandingPayload["campos"]>[number] =>
          value !== null,
      );

    const extras = [...camposAtivos].filter(
      (nome) => !ordemByLower.has(nome.toLowerCase()),
    );
    extras.sort((a, b) => a.localeCompare(b));
    extras.forEach((nome, index) => {
      payload.push({
        nome_campo: nome,
        obrigatorio: camposObrigatorios[nome] ?? true,
        ordem: camposPossiveisUniq.length + index,
      });
    });

    return payload;
  }, [camposAtivos, camposObrigatorios, camposPossiveisUniq]);

  const toggleCampo = useCallback((nome: string) => {
    setCamposAtivos((prev) => {
      const next = new Set(prev);
      const wasActive = next.has(nome);
      if (wasActive) next.delete(nome);
      else next.add(nome);

      if (!wasActive) {
        setCamposObrigatorios((prevObrigatorios) => {
          if (Object.prototype.hasOwnProperty.call(prevObrigatorios, nome))
            return prevObrigatorios;
          return { ...prevObrigatorios, [nome]: true };
        });
      }

      return next;
    });
  }, []);

  const setCampoObrigatorio = useCallback((nome: string, obrigatorio: boolean) => {
    setCamposObrigatorios((prev) => ({ ...prev, [nome]: obrigatorio }));
  }, []);

  const syncFromConfig = useCallback(
    (campos: FormularioCampoInput[] | null | undefined, catalog?: string[]) => {
      const catalogSource = catalog ?? camposPossiveis;
      const catalogByLower = new Map(
        catalogSource.map((nome) => [nome.trim().toLowerCase(), nome.trim()]),
      );
      const nextAtivos = new Set<string>();
      const nextObrigatorios: Record<string, boolean> = {};
      for (const campo of campos || []) {
        const normalized = String(campo?.nome_campo || "").trim();
        if (!normalized) continue;
        const canonical = catalogByLower.get(normalized.toLowerCase()) ?? normalized;
        nextAtivos.add(canonical);
        nextObrigatorios[canonical] = Boolean(campo?.obrigatorio);
      }
      setCamposAtivos(nextAtivos);
      setCamposObrigatorios(nextObrigatorios);
    },
    [camposPossiveis],
  );

  return {
    camposAtivos,
    camposObrigatorios,
    camposPossiveisUniq,
    camposPayload,
    toggleCampo,
    setCampoObrigatorio,
    setCamposAtivos,
    setCamposObrigatorios,
    syncFromConfig,
  };
}
