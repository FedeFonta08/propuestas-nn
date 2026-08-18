import { readFile, readdir, stat } from "node:fs/promises";
import { extname, join, relative } from "node:path";

const root = process.cwd();
const textExtensions = new Set([
  ".css", ".htm", ".html", ".ini", ".js", ".json", ".md",
  ".mjs", ".toml", ".txt", ".xml", ".yaml", ".yml",
]);

const forbiddenPaths = [
  /felicitaciones[_-]?cumple/i,
  /whatsapp[_-]?previos/i,
  /birthday[_-]?automation/i,
  /auth[_-]?drive/i,
  /procesador[_-]?emails/i,
  /google[_-]?apps[_-]?script/i,
  /cockpit[_-]?(?:llamadas|crm|super)/i,
  /nn[_-]?crm[_-]?panel/i,
  /alertas[_-]?cierre/i,
  /mapa[_-]?(?:arquitectura|mental[_-]?ecosistema)/i,
  /(?:^|\/)Briefing_Lunes_ADN\.html$/i,
  /(?:^|\/)panel-despegue[^/]*\.html$/i,
  /(?:^|\/)index_v4_premium\.html$/i,
  /(?:^|\/)radar_db\.json$/i,
  /(?:^|\/)aperturas_desktop_v[4-9][^/]*\.html$/i,
];

const forbiddenContent = [
  ["private key", /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/],
  ["GitHub token", /(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,})/],
  ["Google API key", /AIza[0-9A-Za-z_-]{35}/],
  ["AWS access key", /AKIA[0-9A-Z]{16}/],
  ["OpenAI API key", /sk-(?:proj-)?[A-Za-z0-9_-]{20,}/],
  ["Slack token", /xox[baprs]-[A-Za-z0-9-]{10,}/],
  ["OAuth secret material", /"(?:private_key|refresh_token|client_secret)"\s*:/],
  ["public Apps Script endpoint", /https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec/],
  ["public Google Sheets endpoint", /https:\/\/docs\.google\.com\/spreadsheets\//i],
  ["hard-coded spreadsheet identifier", /(?:SHEET_ID|SPREADSHEET_ID|RADAR_SHEET_ID)\s*=/],
  ["public page calling localhost", /https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d+)?/i],
  ["browser-stored master token", /nn_master_token|localStorage\.(?:getItem|setItem)\([^)]*token/i],
  ["embedded contact list", /(?:const|let|var)\s+contactos?\s*=\s*\[/i],
];

async function* walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === ".git") continue;
    const absolute = join(directory, entry.name);
    if (entry.isDirectory()) yield* walk(absolute);
    else if (entry.isFile()) yield absolute;
  }
}

const findings = [];

for await (const absolute of walk(root)) {
  const path = relative(root, absolute).replaceAll("\\", "/");
  if (path === ".github/scripts/security_audit.mjs") continue;

  for (const pattern of forbiddenPaths) {
    if (pattern.test(path)) findings.push({ path, rule: "forbidden operational path" });
  }

  if (!textExtensions.has(extname(path).toLowerCase())) continue;
  if ((await stat(absolute)).size > 5_000_000) continue;

  const content = await readFile(absolute, "utf8");
  for (const [rule, pattern] of forbiddenContent) {
    if (pattern.test(content)) findings.push({ path, rule });
  }
}

if (findings.length) {
  console.error("Security policy violations:");
  for (const finding of findings) console.error(`- ${finding.path}: ${finding.rule}`);
  process.exit(1);
}

console.log("Security audit passed.");
