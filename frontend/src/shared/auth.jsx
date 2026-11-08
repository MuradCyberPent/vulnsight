import { createContext, useContext, useEffect, useState } from "react";
import { api, clearToken, getToken, setToken } from "./api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());

  useEffect(() => {
    if (!getToken()) return;
    api.me().then(setUser).catch(() => clearToken()).finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const res = await api.login(username, password);
    setToken(res.access_token);
    setUser(res.user);
  }

  async function register(data) {
    await api.register(data);
    await login(data.username, data.password);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Beginner mode: shows plain-English explanations on every finding.
const PrefsContext = createContext(null);
export const usePrefs = () => useContext(PrefsContext);

export function PrefsProvider({ children }) {
  const [beginner, setBeginner] = useState(() => localStorage.getItem("vulnsight_beginner") !== "off");
  useEffect(() => {
    localStorage.setItem("vulnsight_beginner", beginner ? "on" : "off");
  }, [beginner]);
  return <PrefsContext.Provider value={{ beginner, setBeginner }}>{children}</PrefsContext.Provider>;
}
