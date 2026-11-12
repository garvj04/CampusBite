import { createContext, useContext, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    localStorage.getItem("campusbite_token")
  );

  const [role, setRole] = useState(
    localStorage.getItem("campusbite_role")
  );

  const [userId, setUserId] = useState(
    localStorage.getItem("campusbite_user_id")
  );

  const login = async (email, password) => {
    const response = await api.post("/auth/login", {
      email,
      password,
    });

    const { access_token, role, user_id } = response.data;

    localStorage.setItem("campusbite_token", access_token);
    localStorage.setItem("campusbite_role", role);
    localStorage.setItem("campusbite_user_id", user_id);

    setToken(access_token);
    setRole(role);
    setUserId(user_id);

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("campusbite_token");
    localStorage.removeItem("campusbite_role");
    localStorage.removeItem("campusbite_user_id");

    setToken(null);
    setRole(null);
    setUserId(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        role,
        userId,
        login,
        logout,
        isAuthenticated: Boolean(token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
