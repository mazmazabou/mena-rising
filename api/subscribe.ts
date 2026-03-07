import type { VercelRequest, VercelResponse } from "@vercel/node";
import { Resend } from "resend";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { email } = req.body ?? {};

  if (!email || typeof email !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: "Valid email is required" });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const audienceId = process.env.RESEND_AUDIENCE_ID;

  if (!apiKey || !audienceId) {
    return res.status(500).json({ error: "Server configuration error" });
  }

  try {
    const resend = new Resend(apiKey);
    await resend.contacts.create({
      email,
      audienceId,
    });
    return res.status(200).json({ success: true });
  } catch (err: any) {
    if (err?.statusCode === 409) {
      // Already subscribed — treat as success
      return res.status(200).json({ success: true });
    }
    console.error("Resend error:", err);
    return res.status(500).json({ error: "Failed to subscribe" });
  }
}
