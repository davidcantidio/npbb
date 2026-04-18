import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
        // Leitura de lotes (colunas/preview/mapear) pode exceder o defeito do proxy.
        proxyTimeout: 120_000,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;
          if (id.includes("@mui/icons-material")) return "vendor-mui-icons";
          if (id.includes("@mui/") || id.includes("@emotion/")) return "vendor-mui";
          if (id.includes("@fortawesome/")) return "vendor-icons";
          return "vendor-react";
        },
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true,
    clearMocks: true,
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
  },
});
