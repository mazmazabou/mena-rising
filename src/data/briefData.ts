// MENA Rising — Briefing Data
// This object contains all dynamic data for the weekly brief.
// In production, this will be fetched from an API endpoint.

export const briefData = {
  issue: {
    number: "001",
    weekOf: "March 10, 2026",
  },

  ticker: [
    { label: "EGP/USD", value: "49.82", change: -0.3 },
    { label: "Brent Crude", value: "$81.40", change: 1.2 },
    { label: "SAR/USD", value: "3.75", change: 0 },
    { label: "Egypt Inflation", value: "24.1%", change: null },
    { label: "UAE GDP Growth", value: "4.2%", change: null },
    { label: "Morocco CPI", value: "2.8%", change: null },
  ],

  bottomLine:
    "Gulf sovereign wealth funds are accelerating diversification plays as oil price stability breeds confidence. Egypt's currency reform, while painful, is attracting renewed portfolio flows — the EGP has found a floor near 50. Meanwhile, Morocco's green hydrogen ambitions signal a North African pivot toward Europe's energy transition, potentially reshaping Mediterranean trade corridors. Watch Turkey: the lira's controlled descent suggests Ankara is prioritizing export competitiveness over currency stability.",

  macroPulse: [
    { country: "Egypt", flag: "🇪🇬", metric: "Inflation Rate", value: 24.1, unit: "%", change: 0.8, sparkline: [22.1, 22.8, 23.1, 23.5, 23.3, 24.1] },
    { country: "Egypt", flag: "🇪🇬", metric: "EGP/USD", value: 49.82, unit: "", change: -0.3, sparkline: [50.2, 50.5, 50.1, 49.9, 50.0, 49.82] },
    { country: "Saudi Arabia", flag: "🇸🇦", metric: "GDP Growth", value: 2.9, unit: "%", change: 0.2, sparkline: [2.4, 2.5, 2.6, 2.7, 2.8, 2.9] },
    { country: "Saudi Arabia", flag: "🇸🇦", metric: "Oil Revenue", value: 42, unit: "$B", change: 0, sparkline: [41, 42, 41.5, 42, 41.8, 42] },
    { country: "UAE", flag: "🇦🇪", metric: "PMI", value: 55.2, unit: "", change: 1.1, sparkline: [53.1, 53.8, 54.0, 54.5, 54.1, 55.2] },
    { country: "UAE", flag: "🇦🇪", metric: "FDI Inflows", value: 4.1, unit: "$B", change: 3.2, sparkline: [3.5, 3.6, 3.8, 3.9, 4.0, 4.1] },
    { country: "Morocco", flag: "🇲🇦", metric: "CPI", value: 2.8, unit: "%", change: -0.4, sparkline: [3.5, 3.3, 3.2, 3.0, 3.2, 2.8] },
    { country: "Morocco", flag: "🇲🇦", metric: "Tourism Revenue", value: 12, unit: "%", change: 12, sparkline: [5, 6, 7, 8, 10, 12] },
    { country: "Turkey", flag: "🇹🇷", metric: "Inflation", value: 48.2, unit: "%", change: -3.1, sparkline: [55, 54, 52, 51, 51.3, 48.2] },
    { country: "Turkey", flag: "🇹🇷", metric: "Lira/USD", value: 32.1, unit: "", change: -1.2, sparkline: [31.0, 31.3, 31.5, 31.8, 32.0, 32.1] },
    { country: "Qatar", flag: "🇶🇦", metric: "LNG Exports", value: 6.2, unit: "%", change: 6.2, sparkline: [3.1, 3.8, 4.2, 5.0, 5.5, 6.2] },
    { country: "Qatar", flag: "🇶🇦", metric: "Budget Surplus", value: 8.1, unit: "% GDP", change: 0, sparkline: [7.5, 7.8, 7.9, 8.0, 8.0, 8.1] },
  ],

  notableFlows: [
    "Saudi PIF commits $3.5B to NEOM Phase 2 infrastructure",
    "Egypt signs $1.2B IMF tranche, FX reserves stabilize",
    "UAE-India trade corridor hits $85B annual run rate",
    "Morocco green hydrogen MOU with Germany signed",
  ],

  dealsToWatch: [
    { name: "NEOM Phase 2 Infrastructure", parties: "PIF · AECOM · Samsung C&T", value: "$3.5B", status: "Active" },
    { name: "Egypt Ras El-Hekma Development", parties: "ADQ · Egyptian Sovereign Fund", value: "$35B", status: "In Progress" },
    { name: "Morocco-Nigeria Gas Pipeline", parties: "ONHYM · NNPC · ECOWAS", value: "$25B", status: "MOU Signed" },
  ],

  laborSignals: {
    youthUnemployment: [
      { country: "Saudi Arabia", value: 28.6 },
      { country: "Egypt", value: 25.1 },
      { country: "Morocco", value: 22.3 },
      { country: "UAE", value: 7.2 },
      { country: "Qatar", value: 5.8 },
    ],
    aiAdoption: [
      { country: "UAE", rank: 1, score: 72 },
      { country: "Saudi Arabia", rank: 2, score: 65 },
      { country: "Qatar", rank: 3, score: 58 },
      { country: "Egypt", rank: 4, score: 41 },
      { country: "Morocco", rank: 5, score: 34 },
    ],
    techJobs: { trend: "up", change: 18, context: "YoY growth in MENA tech sector postings, driven by UAE and Saudi Arabia giga-project demand." },
  },

  risks: [
    {
      level: "HIGH",
      title: "Egypt FX Pressure",
      description: "Second IMF tranche conditions create political friction; pound volatility expected through Q2. Currency parallel market premium has narrowed but remains a risk indicator.",
      countries: ["Egypt"],
    },
    {
      level: "MEDIUM",
      title: "Red Sea Shipping Disruption",
      description: "Houthi activity continues suppressing Suez Canal revenues, rerouting adds 12-14 days transit. Insurance premiums for Red Sea passages have tripled since Q4 2024.",
      countries: ["Egypt", "Yemen", "Saudi Arabia"],
    },
    {
      level: "LOW",
      title: "Gulf Diversification Execution",
      description: "Vision 2030 / UAE 2071 targets face labor market bottlenecks in technical roles. Reliance on expatriate talent creates structural vulnerability in knowledge economy transition.",
      countries: ["Saudi Arabia", "UAE", "Qatar"],
    },
  ],
};
