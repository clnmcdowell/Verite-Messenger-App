import { defineConfig } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";

const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [sveltekit()],

  // 1. avoid hiding Rust compile errors
  clearScreen: false,

  // 2. front-end dev server settings
  server: {
    port: 5173,
    strictPort: false,
    host: host || false,
    hmr: host ? { protocol: "ws", host, port: 1420 } : undefined,
    watch: {
      // ignore rebuilding on Tauri crate changes
      ignored: ["**/src-tauri/**"],
    },
  },
});
