import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, "");
  const target = (env.VITE_DEV_PROXY_TARGET || "http://127.0.0.1:8000").replace(/\/+$/, "");
  return {
    plugins: [vue()],
    server: {
      port: 5174,
      strictPort: true,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
        },
        "/calculate": {
          target,
          changeOrigin: true,
        },
        "/figures": {
          target,
          changeOrigin: true,
        },
      },
    },
  };
});

