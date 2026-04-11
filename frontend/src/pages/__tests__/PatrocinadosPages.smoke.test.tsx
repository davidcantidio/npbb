import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PatrocinadosListPage from "../../features/patrocinados/PatrocinadosListPage";
import { __clearPatrocinadoresStorageForTests } from "../../services/patrocinados_local";

describe("PatrocinadosPages smoke", () => {
  afterEach(() => {
    __clearPatrocinadoresStorageForTests();
  });

  it("renderiza lista em /patrocinados com aviso e tabela", () => {
    render(
      <MemoryRouter initialEntries={["/patrocinados"]}>
        <Routes>
          <Route path="/patrocinados" element={<PatrocinadosListPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: /patrocinados/i })).toBeInTheDocument();
    expect(
      screen.getByText(/armazenados apenas no seu navegador/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /novo patrocinador/i })).toBeInTheDocument();
  });
});
