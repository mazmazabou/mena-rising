import { defineConfig, loadEnv, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import fs from "fs";
import { componentTagger } from "lovable-tagger";

/**
 * Dev-only plugin that handles /api/subscribe so the form works on localhost.
 * In production, Vercel routes this to the serverless function in api/subscribe.ts.
 */
function apiDevPlugin(): Plugin {
  return {
    name: "api-dev-server",
    configureServer(server) {
      server.middlewares.use("/api/subscribe", async (req, res) => {
        if (req.method !== "POST") {
          res.writeHead(405, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Method not allowed" }));
          return;
        }

        let body = "";
        for await (const chunk of req) body += chunk;

        let email: string;
        try {
          email = JSON.parse(body).email;
        } catch {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Invalid JSON" }));
          return;
        }

        if (!email || typeof email !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Valid email is required" }));
          return;
        }

        // Resolve env: check process.env first, then pipeline/.env as fallback
        let apiKey = process.env.RESEND_API_KEY || "";
        let audienceId = process.env.RESEND_AUDIENCE_ID || "";
        if (!apiKey || !audienceId) {
          try {
            const envFile = fs.readFileSync(path.resolve(__dirname, "pipeline/.env"), "utf-8");
            for (const line of envFile.split("\n")) {
              const m = line.match(/^(RESEND_API_KEY|RESEND_AUDIENCE_ID)=(.+)$/);
              if (m) {
                if (m[1] === "RESEND_API_KEY" && !apiKey) apiKey = m[2].trim();
                if (m[1] === "RESEND_AUDIENCE_ID" && !audienceId) audienceId = m[2].trim();
              }
            }
          } catch {}
        }

        if (!apiKey || !audienceId) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "RESEND_API_KEY and RESEND_AUDIENCE_ID required in .env or pipeline/.env" }));
          return;
        }

        try {
          const { Resend } = await import("resend");
          const resend = new Resend(apiKey);
          await resend.contacts.create({ email, audienceId });
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ success: true }));
        } catch (err: any) {
          if (err?.statusCode === 409) {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ success: true }));
            return;
          }
          console.error("Resend error:", err);
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Failed to subscribe" }));
        }
      });
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
  },
  plugins: [
    react(),
    mode === "development" && componentTagger(),
    mode === "development" && apiDevPlugin(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
