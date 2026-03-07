import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE_URL = "https://mena-rising.com";
const publicDir = path.resolve(__dirname, "../public");
const manifestPath = path.join(publicDir, "data/archive/manifest.json");
const outputPath = path.join(publicDir, "sitemap.xml");

const today = new Date().toISOString().split("T")[0];

let archiveEntries = [];
try {
  archiveEntries = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
} catch {
  console.warn("No manifest.json found — sitemap will omit archive issues.");
}

const urls = [
  { loc: `${SITE_URL}/`, changefreq: "weekly", priority: "1.0", lastmod: today },
  { loc: `${SITE_URL}/archive`, changefreq: "weekly", priority: "0.8", lastmod: today },
  ...archiveEntries.map((entry) => ({
    loc: `${SITE_URL}/archive/${entry.issue}`,
    changefreq: "monthly",
    priority: "0.6",
    lastmod: entry.date,
  })),
];

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${u.lastmod}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`
  )
  .join("\n")}
</urlset>
`;

fs.writeFileSync(outputPath, sitemap);
console.log(`Sitemap generated with ${urls.length} URLs: ${outputPath}`);
