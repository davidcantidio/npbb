/**
 * Persistência local provisória para o módulo Patrocinadores.
 * Substituir por chamadas HTTP (ex.: requestJson em ./http) quando existir /api/patrocinadores/...
 */
import type {
  Contrapartida,
  ContrapartidaInput,
  ContratoPatrocinio,
  ContratoPatrocinioInput,
  Patrocinador,
  PatrocinadorInput,
  PatrocinadorListItem,
} from "../types/patrocinados";

const STORAGE_KEY = "npbb.patrocinados.v1";

type StoreDocument = {
  patrocinadores: Patrocinador[];
};

function nowIso() {
  return new Date().toISOString();
}

function newId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

function emptyStore(): StoreDocument {
  return { patrocinadores: [] };
}

function loadRaw(): StoreDocument {
  if (typeof window === "undefined" || !window.localStorage) {
    return emptyStore();
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyStore();
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || !Array.isArray((parsed as StoreDocument).patrocinadores)) {
      return emptyStore();
    }
    return parsed as StoreDocument;
  } catch {
    return emptyStore();
  }
}

function saveDoc(doc: StoreDocument) {
  if (typeof window === "undefined" || !window.localStorage) return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(doc));
}

function toListItem(p: Patrocinador): PatrocinadorListItem {
  return {
    id: p.id,
    nome_fantasia: p.nome_fantasia,
    razao_social: p.razao_social,
    cnpj: p.cnpj,
    email: p.email,
    ativo: p.ativo,
    created_at: p.created_at,
    updated_at: p.updated_at,
    contrapartidas_count: p.contrapartidas.length,
    contratos_count: p.contratos.length,
  };
}

export function listPatrocinadores(): PatrocinadorListItem[] {
  return loadRaw().patrocinadores.map(toListItem);
}

export function getPatrocinador(id: string): Patrocinador | null {
  const p = loadRaw().patrocinadores.find((x) => x.id === id);
  return p ? { ...p, contrapartidas: [...p.contrapartidas], contratos: [...p.contratos] } : null;
}

export function createPatrocinador(input: PatrocinadorInput): Patrocinador {
  const doc = loadRaw();
  const ts = nowIso();
  const entity: Patrocinador = {
    ...input,
    id: newId(),
    created_at: ts,
    updated_at: ts,
    contrapartidas: [],
    contratos: [],
  };
  doc.patrocinadores.push(entity);
  saveDoc(doc);
  return { ...entity };
}

export function updatePatrocinador(id: string, input: PatrocinadorInput): Patrocinador | null {
  const doc = loadRaw();
  const idx = doc.patrocinadores.findIndex((x) => x.id === id);
  if (idx < 0) return null;
  const prev = doc.patrocinadores[idx];
  const next: Patrocinador = {
    ...prev,
    ...input,
    id: prev.id,
    created_at: prev.created_at,
    updated_at: nowIso(),
    contrapartidas: prev.contrapartidas,
    contratos: prev.contratos,
  };
  doc.patrocinadores[idx] = next;
  saveDoc(doc);
  return { ...next, contrapartidas: [...next.contrapartidas], contratos: [...next.contratos] };
}

export function deletePatrocinador(id: string): boolean {
  const doc = loadRaw();
  const before = doc.patrocinadores.length;
  doc.patrocinadores = doc.patrocinadores.filter((x) => x.id !== id);
  if (doc.patrocinadores.length === before) return false;
  saveDoc(doc);
  return true;
}

export function upsertContrapartida(
  patrocinadorId: string,
  contrapartidaId: string | null,
  input: ContrapartidaInput,
): Contrapartida | null {
  const doc = loadRaw();
  const pIdx = doc.patrocinadores.findIndex((x) => x.id === patrocinadorId);
  if (pIdx < 0) return null;
  const p = doc.patrocinadores[pIdx];
  const ts = nowIso();

  if (contrapartidaId) {
    const cIdx = p.contrapartidas.findIndex((c) => c.id === contrapartidaId);
    if (cIdx < 0) return null;
    const updated: Contrapartida = {
      ...p.contrapartidas[cIdx],
      ...input,
      id: contrapartidaId,
      patrocinador_id: patrocinadorId,
      updated_at: ts,
    };
    p.contrapartidas[cIdx] = updated;
  } else {
    const created: Contrapartida = {
      ...input,
      id: newId(),
      patrocinador_id: patrocinadorId,
      created_at: ts,
      updated_at: ts,
    };
    p.contrapartidas.push(created);
  }
  p.updated_at = ts;
  doc.patrocinadores[pIdx] = p;
  saveDoc(doc);
  const list = p.contrapartidas;
  return contrapartidaId
    ? list.find((c) => c.id === contrapartidaId) ?? null
    : list[list.length - 1] ?? null;
}

export function deleteContrapartida(patrocinadorId: string, contrapartidaId: string): boolean {
  const doc = loadRaw();
  const pIdx = doc.patrocinadores.findIndex((x) => x.id === patrocinadorId);
  if (pIdx < 0) return false;
  const p = doc.patrocinadores[pIdx];
  const before = p.contrapartidas.length;
  p.contrapartidas = p.contrapartidas.filter((c) => c.id !== contrapartidaId);
  if (p.contrapartidas.length === before) return false;
  p.updated_at = nowIso();
  saveDoc(doc);
  return true;
}

export function upsertContrato(
  patrocinadorId: string,
  contratoId: string | null,
  input: ContratoPatrocinioInput,
): ContratoPatrocinio | null {
  const doc = loadRaw();
  const pIdx = doc.patrocinadores.findIndex((x) => x.id === patrocinadorId);
  if (pIdx < 0) return null;
  const p = doc.patrocinadores[pIdx];
  const ts = nowIso();

  if (contratoId) {
    const cIdx = p.contratos.findIndex((c) => c.id === contratoId);
    if (cIdx < 0) return null;
    const updated: ContratoPatrocinio = {
      ...p.contratos[cIdx],
      ...input,
      id: contratoId,
      patrocinador_id: patrocinadorId,
      updated_at: ts,
    };
    p.contratos[cIdx] = updated;
  } else {
    const created: ContratoPatrocinio = {
      ...input,
      id: newId(),
      patrocinador_id: patrocinadorId,
      created_at: ts,
      updated_at: ts,
    };
    p.contratos.push(created);
  }
  p.updated_at = ts;
  doc.patrocinadores[pIdx] = p;
  saveDoc(doc);
  const list = p.contratos;
  return contratoId ? list.find((c) => c.id === contratoId) ?? null : list[list.length - 1] ?? null;
}

export function deleteContrato(patrocinadorId: string, contratoId: string): boolean {
  const doc = loadRaw();
  const pIdx = doc.patrocinadores.findIndex((x) => x.id === patrocinadorId);
  if (pIdx < 0) return false;
  const p = doc.patrocinadores[pIdx];
  const before = p.contratos.length;
  p.contratos = p.contratos.filter((c) => c.id !== contratoId);
  if (p.contratos.length === before) return false;
  p.updated_at = nowIso();
  saveDoc(doc);
  return true;
}

/** Apenas para testes: limpar o armazenamento local. */
export function __clearPatrocinadoresStorageForTests() {
  if (typeof window !== "undefined" && window.localStorage) {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}
