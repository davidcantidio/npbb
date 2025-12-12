import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as apiLogin, LoginUser } from "../services/auth";

type AuthContextValue = {
  user: LoginUser | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<LoginUser>;
  logout: () => void;
  refresh: () => Promise<LoginUser | null>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "access_token";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<LoginUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        setError(err?.message || "Nao foi possivel validar a sessao");
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogin = async (email: string, password: string) => {
    setError(null);
    const res = await apiLogin({ email, password });
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError(null);
  };

  const refresh = async () => {
    if (!token) return null;
    try {
      const me = await getMe(token);
      setUser(me);
      setError(null);
      return me;
    } catch (err: any) {
      setError(err?.message || "Nao foi possivel atualizar os dados");
      return null;
    }
  };

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      error,
      login: handleLogin,
      logout: handleLogout,
      refresh,
    }),
    [user, token, loading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
}
