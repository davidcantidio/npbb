import { describe, expect, it } from "vitest";
import * as legacy from "../../eventos";
import * as modular from "../index";

describe("eventos legacy barrel compatibility", () => {
  it("re-exports core/form/workflow symbols", () => {
    expect(legacy.createEvento).toBe(modular.createEvento);
    expect(legacy.getEventoFormConfig).toBe(modular.getEventoFormConfig);
    expect(legacy.listEventoGamificacoes).toBe(modular.listEventoGamificacoes);
    expect(legacy.listEventoAtivacoes).toBe(modular.listEventoAtivacoes);
  });
});
