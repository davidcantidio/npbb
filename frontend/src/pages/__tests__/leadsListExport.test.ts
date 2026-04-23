import { describe, expect, it } from "vitest";

import type { LeadListItem } from "../../services/leads_import";
import {
  buildLeadsListCsvContent,
  getLeadListCsvCells,
  LEADS_LIST_CSV_HEADERS,
  resolveLeadListExportEvent,
} from "../../features/leads/list";

function makeLead(overrides: Partial<LeadListItem> = {}): LeadListItem {
  return {
    id: 1,
    nome: "User 1",
    sobrenome: null,
    email: "user1@example.com",
    cpf: "12345678900",
    telefone: "11999990000",
    evento_nome: "Evento de origem",
    cidade: "Sao Paulo",
    estado: "SP",
    data_compra: null,
    data_criacao: "2026-01-15T12:00:00.000Z",
    evento_convertido_id: 2,
    evento_convertido_nome: "Evento convertido",
    tipo_conversao: null,
    data_conversao: null,
    rg: null,
    genero: "Feminino",
    is_cliente_bb: false,
    is_cliente_estilo: null,
    logradouro: null,
    numero: null,
    complemento: null,
    bairro: null,
    cep: null,
    data_nascimento: "2000-06-20",
    data_evento: "2025-02-04 00:00:00",
    soma_de_ano_evento: 2025,
    tipo_evento: "Esporte",
    local_evento: "Navegantes-SC",
    faixa_etaria: "18-40",
    soma_de_idade: 25,
    ...overrides,
  };
}

describe("leadsListExport", () => {
  it("prefere o evento da conversao quando existir", () => {
    const row = makeLead();

    expect(resolveLeadListExportEvent(row)).toBe("Evento convertido");
    expect(getLeadListCsvCells(row)[6]).toBe("Evento convertido");
  });

  it("faz fallback para o evento de origem quando nao houver conversao", () => {
    const row = makeLead({
      evento_convertido_id: null,
      evento_convertido_nome: null,
      data_evento: null,
      tipo_evento: null,
    });

    expect(resolveLeadListExportEvent(row)).toBe("Evento de origem");
    expect(getLeadListCsvCells(row)).toEqual([
      "User 1",
      "12345678900",
      "6/20/2000",
      "user1@example.com",
      "11999990000",
      "",
      "Evento de origem",
      "Navegantes-SC",
      "",
    ]);
  });

  it("mantem BOM, CRLF, escaping e cardinalidade das colunas", () => {
    const row = makeLead({
      nome: 'User "A", teste',
      local_evento: "Rio,\nJaneiro-RJ",
      origem: 'Proponente "teste"',
      data_evento: "2025-06-28T00:00:00Z",
    });

    const csv = buildLeadsListCsvContent([row]);

    expect(csv.startsWith("\uFEFF")).toBe(true);
    expect(csv).toContain("\r\n");

    const lines = csv.slice(1).split("\r\n");
    expect(lines[0]).toBe(LEADS_LIST_CSV_HEADERS.join(","));
    expect(lines).toHaveLength(2);

    const values = getLeadListCsvCells(row);
    expect(values).toHaveLength(LEADS_LIST_CSV_HEADERS.length);
    expect(lines[1]).toContain('"User ""A"", teste"');
    expect(lines[1]).toContain('"Rio,');
    expect(lines[1]).toContain('Proponente ""teste""');
    expect(lines[1]).toContain("6/28/2025");
  });
});
