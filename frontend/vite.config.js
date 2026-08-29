import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/frontend-config": "http://127.0.0.1:5000",
      "/process-file": "http://127.0.0.1:5000",
      "/process-live-speech": "http://127.0.0.1:5000",
      "/generated-audio": "http://127.0.0.1:5000",
      "/test-file": "http://127.0.0.1:5000"
    }
  },
  build: {
    outDir: resolve(__dirname, "../static/app"),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: "assets/app.js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: ({ name }) => {
          if (name && name.endsWith(".css")) {
            return "assets/app.css";
          }
          return "assets/[name][extname]";
        }
      }
    }
  }
});
