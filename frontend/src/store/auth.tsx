import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as apiLogin, LoginUser, logout as apiLogout, refreshSession } from "../services/auth";

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
    setToken(null);
    setUser(null);
    setError(message || null);
  }, []);

  useEffect(() => {
    setLoading(true);
    getMe()
      .then(async (me) => {
        setUser(me);
        setError(null);
        try {
          const refreshed = await refreshSession();
          setToken(refreshed.access_token || null);
        } catch {
          setToken(null);
        }
      })
      .catch((err: any) => {
        clearSession(err?.message || "Sessao invalida. Faca login novamente.");
      })
      .finally(() => setLoading(false));
  }, [clearSession]);

  const handleLogin = async (email: string, password: string) => {
    setError(null);
    const res = await apiLogin({ email, password });
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const handleLogout = () => {
    void apiLogout().finally(() => clearSession());
  };

  const refresh = useCallback(async () => {
    if (refreshing) return null;
    setRefreshing(true);
    try {
      const refreshed = await refreshSession(token);
      setToken(refreshed.access_token || null);
      setUser(refreshed.user);
      setError(null);
      return refreshed.user;
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
