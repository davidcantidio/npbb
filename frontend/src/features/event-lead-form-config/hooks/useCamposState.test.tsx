import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useCamposState } from "./useCamposState";

describe("useCamposState", () => {
  it("preselects default fields and keeps CPF locked when config is empty", () => {
    const catalog = ["CPF", "Nome", "Sobrenome", "Data de nascimento", "Email"];
    const { result } = renderHook(() => useCamposState(catalog));

    act(() => {
      result.current.syncFromConfig([], catalog);
    });

    expect(result.current.camposAtivosOrdenados).toEqual([
      "CPF",
      "Nome",
      "Sobrenome",
      "Data de nascimento",
    ]);
    expect(result.current.camposDisponiveis).toEqual(["Email"]);
    expect(result.current.camposPayload).toEqual([
      { nome_campo: "CPF", obrigatorio: true, ordem: 0 },
      { nome_campo: "Nome", obrigatorio: true, ordem: 1 },
      { nome_campo: "Sobrenome", obrigatorio: true, ordem: 2 },
      { nome_campo: "Data de nascimento", obrigatorio: true, ordem: 3 },
    ]);

    act(() => {
      result.current.toggleCampo("CPF");
      result.current.setCampoObrigatorio("CPF", false);
    });

    expect(result.current.camposAtivosOrdenados).toContain("CPF");
    expect(result.current.camposPayload[0]).toEqual({
      nome_campo: "CPF",
      obrigatorio: true,
      ordem: 0,
    });
  });

  it("reorders active fields and persists the new payload order", () => {
    const catalog = ["CPF", "Nome", "Email", "Sobrenome"];
    const { result } = renderHook(() => useCamposState(catalog));

    act(() => {
      result.current.syncFromConfig(
        [
          { nome_campo: "CPF", obrigatorio: true, ordem: 0 },
          { nome_campo: "Nome", obrigatorio: true, ordem: 1 },
          { nome_campo: "Email", obrigatorio: true, ordem: 2 },
        ],
        catalog,
      );
    });

    act(() => {
      result.current.reorderCampoAtivo("Email", "Nome");
    });

    expect(result.current.camposAtivosOrdenados).toEqual(["CPF", "Email", "Nome"]);
    expect(result.current.camposPayload).toEqual([
      { nome_campo: "CPF", obrigatorio: true, ordem: 0 },
      { nome_campo: "Email", obrigatorio: true, ordem: 1 },
      { nome_campo: "Nome", obrigatorio: true, ordem: 2 },
    ]);
  });
});
