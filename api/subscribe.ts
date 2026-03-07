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

    return res.status(200).json({ success: true });
  } catch (err: any) {
    if (err?.statusCode === 409) {
      // Already subscribed — treat as success, no welcome email
      return res.status(200).json({ success: true });
    }
    console.error("Resend error:", err);
    return res.status(500).json({ error: "Failed to subscribe" });
  }
}
