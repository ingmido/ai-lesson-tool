import { defineStore } from "pinia";
import api from "../api/axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: JSON.parse(localStorage.getItem("user") || "null"),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === "admin",
  },
  actions: {
    setSession(token, user) {
      this.token = token;
      this.user = user;
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
    },
    async login(username, password) {
      const { data } = await api.post("/auth/login", { username, password });
      this.setSession(data.token, data.user);
      return data.user;
    },
    async register(formData) {
      const { data } = await api.post("/auth/register", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      this.setSession(data.token, data.user);
      return data.user;
    },
    async refreshMe() {
      const { data } = await api.get("/profile/me");
      this.user = data;
      localStorage.setItem("user", JSON.stringify(data));
      return data;
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
});
