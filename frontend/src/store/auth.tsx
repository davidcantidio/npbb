import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as apiLogin, LoginUser } from "../services/auth";

type AuthContextValue = {
  user: LoginUser | null;
  token: string | null;
  loading: boolean;
  refreshing: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<LoginUser>;
  logout: () => void;
  refresh: () => Promise<LoginUser | null>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "access_token";

/**
 * Provides authentication state and session lifecycle handlers for the app.
 * @param params.children React subtree that needs auth context.
 * @returns Context provider with session state and auth actions.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<LoginUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearSession = useCallback((message?: string) => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError(message || null);
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setLoading(false);
      return;
    }
    setToken(stored);
    setLoading(true);
    getMe(stored)
      .then((me) => {
        setUser(me);
        setError(null);
      })
      .catch((err: any) => {
        clearSession(err?.message || "Sessao invalida. Faca login novamente.");
      })
      .finally(() => setLoading(false));
  }, [clearSession]);

  const handleLogin = async (email: string, password: string) => {
    setError(null);
    const res = await apiLogin({ email, password });
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const handleLogout = () => clearSession();

  const refresh = useCallback(async () => {
    if (!token) return null;
    if (refreshing) return null;
    setRefreshing(true);
    try {
      const me = await getMe(token);
      setUser(me);
      setError(null);
      return me;
    } catch (err: any) {
      clearSession(err?.message || "Sessao expirada. Faca login novamente.");
      return null;
    } finally {
      setRefreshing(false);
    }
  }, [clearSession, refreshing, token]);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      refreshing,
      error,
      login: handleLogin,
      logout: handleLogout,
      refresh,
    }),
    [user, token, loading, refreshing, error, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Accesses the current auth context. Must be used within `AuthProvider`.
 * @returns Auth context value with session state and actions.
 * @throws Error When called outside `AuthProvider`.
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
}
