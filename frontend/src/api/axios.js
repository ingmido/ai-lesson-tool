import axios from "axios";

// In dev, Vite proxies "/api" to localhost:5000 (see vite.config.js).
// In production the frontend and backend are usually deployed separately,
// so set VITE_API_BASE_URL (e.g. https://your-backend.onrender.com) at build time.
export const API_ORIGIN = import.meta.env.VITE_API_BASE_URL || "";

const api = axios.create({
  baseURL: `${API_ORIGIN}/api`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
