import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import {
  ThemeModeProvider,
  useThemeMode,
} from "../ThemeModeProvider";
import { APP_THEME_MODE_STORAGE_KEY } from "../index";

function mockMatchMedia(matches: boolean) {
  const listeners = new Set<(event: MediaQueryListEvent) => void>();
  const mediaQueryList = {
    matches,
    media: "(prefers-color-scheme: dark)",
    onchange: null,
    addEventListener: vi.fn((_event: string, listener: (event: MediaQueryListEvent) => void) => {
      listeners.add(listener);
    }),
    removeEventListener: vi.fn((_event: string, listener: (event: MediaQueryListEvent) => void) => {
      listeners.delete(listener);
    }),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  };

  vi.stubGlobal("matchMedia", vi.fn().mockImplementation(() => mediaQueryList));

  return {
    emit(nextMatches: boolean) {
      mediaQueryList.matches = nextMatches;
      listeners.forEach((listener) => listener({ matches: nextMatches } as MediaQueryListEvent));
    },
  };
}

function ThemeModeProbe() {
  const { mode, resolvedMode, setMode, toggleMode } = useThemeMode();

  return (
    <>
      <div data-testid="mode">{mode}</div>
      <div data-testid="resolved-mode">{resolvedMode}</div>
      <button type="button" onClick={() => setMode("system")}>
        system
      </button>
      <button type="button" onClick={toggleMode}>
        toggle
      </button>
    </>
  );
}

describe("ThemeModeProvider", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("usa o fallback do sistema quando nao ha preferencia persistida", () => {
    mockMatchMedia(true);

    render(
      <ThemeModeProvider>
        <ThemeModeProbe />
      </ThemeModeProvider>,
    );

    expect(screen.getByTestId("mode")).toHaveTextContent("system");
    expect(screen.getByTestId("resolved-mode")).toHaveTextContent("dark");
  });

  it("prioriza o valor persistido em localStorage", () => {
    window.localStorage.setItem(APP_THEME_MODE_STORAGE_KEY, "light");
    mockMatchMedia(true);

    render(
      <ThemeModeProvider>
        <ThemeModeProbe />
      </ThemeModeProvider>,
    );

    expect(screen.getByTestId("mode")).toHaveTextContent("light");
    expect(screen.getByTestId("resolved-mode")).toHaveTextContent("light");
  });

  it("persiste o toggle e atualiza o modo resolvido", async () => {
    const user = userEvent.setup();
    const media = mockMatchMedia(false);

    render(
      <ThemeModeProvider>
        <ThemeModeProbe />
      </ThemeModeProvider>,
    );

    await user.click(screen.getByRole("button", { name: "toggle" }));

    expect(screen.getByTestId("mode")).toHaveTextContent("dark");
    expect(screen.getByTestId("resolved-mode")).toHaveTextContent("dark");
    expect(window.localStorage.getItem(APP_THEME_MODE_STORAGE_KEY)).toBe("dark");

    await user.click(screen.getByRole("button", { name: "system" }));
    act(() => {
      media.emit(true);
    });

    expect(screen.getByTestId("mode")).toHaveTextContent("system");
    await waitFor(() => {
      expect(screen.getByTestId("resolved-mode")).toHaveTextContent("dark");
    });
    expect(window.localStorage.getItem(APP_THEME_MODE_STORAGE_KEY)).toBe("system");
  });
});
