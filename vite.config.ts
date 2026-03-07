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

          // Fire-and-forget welcome email for new subscribers
          try {
            await resend.emails.send({
              from: "MENA Rising <brief@mena-rising.com>",
              to: [email],
              subject: "Welcome to MENA Rising",
              html: `<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 560px; margin: 0 auto; color: #1a1a2e;">
  <h1 style="font-size: 24px; color: #c9a84c; margin-bottom: 16px;">Welcome to MENA Rising</h1>
  <p style="font-size: 16px; line-height: 1.6;">You're now on the list for the sharpest weekly briefing on the Middle East &amp; North Africa economy.</p>
  <p style="font-size: 16px; line-height: 1.6;">Every <strong>Monday</strong>, you'll receive a concise rundown of macro trends, trade flows, labor signals, and risk analysis across the region — all in one read.</p>
  <p style="font-size: 16px; line-height: 1.6;">Keep an eye on your inbox.</p>
  <p style="font-size: 14px; color: #666; margin-top: 32px;">— The MENA Rising Team</p>
</div>`,
            });
          } catch (emailErr) {
            console.error("Welcome email failed:", emailErr);
          }

          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ success: true }));
        } catch (err: any) {
          if (err?.statusCode === 409) {
            // Already subscribed — no welcome email
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ success: true, already: true }));
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
