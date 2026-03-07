import sharp from "sharp";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputPath = path.resolve(__dirname, "../public/og-default.png");

const WIDTH = 1200;
const HEIGHT = 630;

// Ottoman-inspired OG image: dark navy background, gold masthead, geometric motif
const svg = `
<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a0a1a"/>
      <stop offset="100%" stop-color="#0f1629"/>
    </linearGradient>
    <!-- Geometric star pattern -->
    <pattern id="stars" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
      <polygon points="40,10 45,30 65,30 49,42 55,62 40,50 25,62 31,42 15,30 35,30"
               fill="none" stroke="#c9a84c" stroke-width="0.5" opacity="0.08"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#bg)"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#stars)"/>

  <!-- Top decorative strip -->
  <rect x="0" y="0" width="${WIDTH}" height="6" fill="#c9a84c"/>
  <rect x="0" y="6" width="${WIDTH}" height="2" fill="#c9a84c" opacity="0.3"/>

  <!-- Bottom decorative strip -->
  <rect x="0" y="622" width="${WIDTH}" height="2" fill="#c9a84c" opacity="0.3"/>
  <rect x="0" y="624" width="${WIDTH}" height="6" fill="#c9a84c"/>

  <!-- Left ornamental line -->
  <rect x="60" y="40" width="1" height="550" fill="#c9a84c" opacity="0.15"/>
  <!-- Right ornamental line -->
  <rect x="1139" y="40" width="1" height="550" fill="#c9a84c" opacity="0.15"/>

  <!-- Diamond ornament top center -->
  <polygon points="600,50 610,65 600,80 590,65" fill="#c9a84c" opacity="0.3"/>

  <!-- Masthead -->
  <text x="600" y="240" text-anchor="middle"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="72" font-weight="bold" fill="#c9a84c"
        letter-spacing="6">MENA RISING</text>

  <!-- Ornamental divider -->
  <line x1="350" y1="270" x2="550" y2="270" stroke="#c9a84c" stroke-width="1" opacity="0.5"/>
  <polygon points="600,262 608,270 600,278 592,270" fill="#c9a84c" opacity="0.6"/>
  <line x1="650" y1="270" x2="850" y2="270" stroke="#c9a84c" stroke-width="1" opacity="0.5"/>

  <!-- Tagline -->
  <text x="600" y="330" text-anchor="middle"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="24" fill="#e0d5c1" letter-spacing="3"
        opacity="0.85">Weekly Economic Intelligence Briefing</text>

  <!-- Subtitle -->
  <text x="600" y="390" text-anchor="middle"
        font-family="'Courier New', monospace"
        font-size="16" fill="#c9a84c" opacity="0.5"
        letter-spacing="4">9 ECONOMIES &#x00B7; MACRO &#x00B7; TRADE &#x00B7; RISK</text>

  <!-- Diamond ornament bottom center -->
  <polygon points="600,550 610,565 600,580 590,565" fill="#c9a84c" opacity="0.3"/>
</svg>`;

await sharp(Buffer.from(svg)).png().toFile(outputPath);
console.log(`OG image generated: ${outputPath}`);
