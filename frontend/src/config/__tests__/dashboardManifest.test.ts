import { describe, expect, it } from "vitest";

import { DASHBOARD_MANIFEST } from "../dashboardManifest";

describe("DASHBOARD_MANIFEST", () => {
  it("defines the required dashboard entries with the expected shape", () => {
    expect(DASHBOARD_MANIFEST.length).toBeGreaterThanOrEqual(3);

    for (const entry of DASHBOARD_MANIFEST) {
      expect(entry).toEqual(
        expect.objectContaining({
          id: expect.any(String),
          route: expect.any(String),
          domain: expect.any(String),
          name: expect.any(String),
          icon: expect.any(String),
          description: expect.any(String),
          enabled: expect.any(Boolean),
        }),
      );
    }
  });

  it("keeps the age analysis entry enabled and backlog entries disabled", () => {
    expect(
      DASHBOARD_MANIFEST.find((entry) => entry.route === "/dashboard/leads/analise-etaria"),
    ).toEqual(expect.objectContaining({ enabled: true }));

    expect(
      DASHBOARD_MANIFEST.find((entry) => entry.route === "/dashboard/eventos/fechamento"),
    ).toEqual(expect.objectContaining({ enabled: false }));

    expect(
      DASHBOARD_MANIFEST.find((entry) => entry.route === "/dashboard/leads/conversao"),
    ).toEqual(expect.objectContaining({ enabled: false }));
  });
});
