import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { APP_THEME_MODE_STORAGE_KEY, type PaletteMode } from "./shared";

export type ThemeModeSetting = PaletteMode | "system";

type ThemeModeContextValue = {
  mode: ThemeModeSetting;
  resolvedMode: PaletteMode;
  setMode: (nextMode: ThemeModeSetting) => void;
  toggleMode: () => void;
};

const ThemeModeContext = createContext<ThemeModeContextValue | undefined>(undefined);

function getSystemMode(): PaletteMode {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return "light";
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getStoredMode(): ThemeModeSetting {
  if (typeof window === "undefined") {
    return "system";
  }

  const stored = window.localStorage.getItem(APP_THEME_MODE_STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }

  return "system";
}

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeModeSetting>(() => getStoredMode());
  const [systemMode, setSystemMode] = useState<PaletteMode>(() => getSystemMode());

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return undefined;
    }

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = (event: MediaQueryListEvent) => {
      setSystemMode(event.matches ? "dark" : "light");
    };

    setSystemMode(media.matches ? "dark" : "light");
    media.addEventListener("change", listener);

    return () => {
      media.removeEventListener("change", listener);
    };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    window.localStorage.setItem(APP_THEME_MODE_STORAGE_KEY, mode);
  }, [mode]);

  const resolvedMode = mode === "system" ? systemMode : mode;

  const toggleMode = useCallback(() => {
    setMode((currentMode: ThemeModeSetting) => {
      const effectiveMode = currentMode === "system" ? systemMode : currentMode;
      return effectiveMode === "dark" ? "light" : "dark";
    });
  }, [systemMode]);

  const value = useMemo(
    () => ({
      mode,
      resolvedMode,
      setMode,
      toggleMode,
    }),
    [mode, resolvedMode, toggleMode],
  );

  return <ThemeModeContext.Provider value={value}>{children}</ThemeModeContext.Provider>;
}

export function useThemeMode() {
  const context = useContext(ThemeModeContext);
  if (!context) {
    throw new Error("useThemeMode deve ser usado dentro de ThemeModeProvider");
  }

  return context;
}
