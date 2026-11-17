import { defineConfig } from "vite";
import { execSync } from "node:child_process";
let ver = "dev";
try { ver = execSync("git rev-parse --short HEAD").toString().trim(); } catch {}
export default defineConfig({
  base: "./",
  define: { "import.meta.env.VITE_VERSION": JSON.stringify("0.1-" + ver) },
  build: { target: "es2019", assetsInlineLimit: 0, chunkSizeWarningLimit: 600, reportCompressedSize: false },
  server: { host: "127.0.0.1", port: 5193, strictPort: true },
});
