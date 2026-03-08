import { describe, expect, it } from "vitest";

import { getCoverageStatus, hasPartialBbData } from "../coverage";

describe("coverage utils", () => {
  it("classifies coverage thresholds correctly", () => {
    expect(getCoverageStatus(80)).toBe("normal");
    expect(getCoverageStatus(79.9)).toBe("warning");
    expect(getCoverageStatus(20)).toBe("warning");
    expect(getCoverageStatus(19.9)).toBe("danger");
  });

  it("flags partial BB data only when BB metrics are null under low coverage", () => {
    expect(hasPartialBbData(null, null, 60)).toBe(true);
    expect(hasPartialBbData(null, null, 10)).toBe(true);
    expect(hasPartialBbData(20, 50, 60)).toBe(false);
    expect(hasPartialBbData(null, null, 100)).toBe(false);
  });
});
