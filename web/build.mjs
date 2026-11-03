#!/usr/bin/env node
/**
 * build.mjs — 단일 HTML 파일 빌드 (의존성 없음, Node 18+)
 *
 * 사용법
 *   node build.mjs                      # 일반 제출용  → dist/independence-review.html
 *   node build.mjs --out ../static/independence-review.html
 *   node build.mjs --brand pwc --brand-dir ../internal/pwc \
 *     --out ../internal/pwc/dist/independence-review.pwc.html
 *   node build.mjs --mermaid cdn|local|inline
 *
 * 규칙
 *   - 일반 패키지(web/)에는 brand.pwc.* / PwC 로고를 두지 않는다.
 *   - PwC 브랜드는 --brand-dir 로 외부 디렉터리만 참조한다.
 *   - 소스(core.html)는 수정하지 않는다.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const MERMAID_VERSION = "10.9.8";

/* ── 인자 파싱 ─────────────────────────────────────────── */
const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};
const brandId = opt("brand", "default");
const mermaidMode = opt("mermaid", "inline");
const brandDirArg = opt("brand-dir", null);
if (!/^[a-z0-9-]+$/i.test(brandId)) fail(`잘못된 --brand 값: ${brandId}`);
if (!["inline", "cdn", "local"].includes(mermaidMode)) fail(`잘못된 --mermaid 값: ${mermaidMode}`);

const brandDir = brandDirArg
  ? path.resolve(ROOT, brandDirArg)
  : ROOT;
if (!fs.existsSync(brandDir) || !fs.statSync(brandDir).isDirectory()) {
  fail(`--brand-dir 디렉터리가 없습니다: ${brandDir}`);
}

const brandFileName = brandId === "default" ? "brand.json" : `brand.${brandId}.json`;
const brandFileRel = path.relative(ROOT, path.join(brandDir, brandFileName)) || brandFileName;
const outFile = path.resolve(
  ROOT,
  opt("out", `dist/independence-review${brandId === "default" ? "" : "." + brandId}.html`),
);

function fail(message) {
  console.error("✖ " + message);
  process.exit(1);
}
const readRoot = (rel) => {
  const file = path.join(ROOT, rel);
  if (!fs.existsSync(file)) fail(`파일이 없습니다: ${rel}`);
  return fs.readFileSync(file, "utf8");
};
const readBrandPath = (absOrRel) => {
  const file = path.isAbsolute(absOrRel) ? absOrRel : path.join(brandDir, absOrRel);
  if (!fs.existsSync(file)) fail(`브랜드 파일이 없습니다: ${path.relative(ROOT, file)}`);
  return { file, text: fs.readFileSync(file, "utf8") };
};
/** <script> 안에 넣어도 HTML 파서가 종료·오인하지 않도록 이스케이프 (JS 의미는 동일) */
const escapeForScript = (code) => code.replace(/<\/script/gi, "<\\/script").replace(/<!--/g, "<\\!--");

/* ── 입력 로드 ─────────────────────────────────────────── */
let html = readRoot("core.html");
const brand = JSON.parse(readBrandPath(brandFileName).text);

/* 1) 테마 CSS 인라인 */
let css = readRoot("theme.css");
if (brand.theme) {
  const themePath = path.isAbsolute(brand.theme)
    ? brand.theme
    : path.join(brandDir, brand.theme);
  const { text: themeCss } = readBrandPath(themePath);
  css += `\n/* ── brand theme: ${path.basename(themePath)} ── */\n` + themeCss;
  brand.theme = null; // 이미 인라인했으므로 런타임 로드 불필요
}
const LINK = /<link rel="stylesheet" href="theme\.css" \/>/;
if (!LINK.test(html)) fail('core.html 에서 <link rel="stylesheet" href="theme.css" /> 를 찾지 못했습니다.');
html = html.replace(LINK, () => `<style id="theme-tokens">\n${css}\n</style>`);

/* 2) 로고 인라인 */
const MIME = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp" };
if (brand.logo && brand.logo.src && !/^(https:|data:)/i.test(brand.logo.src)) {
  const file = path.isAbsolute(brand.logo.src)
    ? brand.logo.src
    : path.join(brandDir, brand.logo.src);
  const mime = MIME[path.extname(file).toLowerCase()];
  if (mime && fs.existsSync(file)) {
    brand.logo.src = `data:${mime};base64,` + fs.readFileSync(file).toString("base64");
  } else {
    console.warn(`⚠ 로고를 찾을 수 없어 텍스트 마크로 대체합니다: ${brand.logo.src}`);
    brand.logo.src = null;
  }
}

/* 3) Mermaid */
const vendorPath = path.join(ROOT, "vendor/mermaid.min.js");
if (!fs.existsSync(vendorPath)) fail("vendor/mermaid.min.js 가 없습니다.");
const vendorBytes = fs.readFileSync(vendorPath);
const sri = "sha384-" + crypto.createHash("sha384").update(vendorBytes).digest("base64");
const recorded = readRoot("vendor/mermaid.min.js.sha384").trim();
if (sri !== recorded) fail(`vendor/mermaid.min.js 무결성 불일치\n  계산값: ${sri}\n  기록값: ${recorded}`);

const MERMAID_TAG = '<script src="vendor/mermaid.min.js"></script>';
if (!html.includes(MERMAID_TAG)) fail("core.html 에서 Mermaid <script> 태그를 찾지 못했습니다.");
const mermaidReplacement = {
  inline: () => `<script>/* mermaid@${MERMAID_VERSION} (MIT) */\n${escapeForScript(vendorBytes.toString("utf8"))}\n</script>`,
  cdn: () =>
    `<script src="https://cdn.jsdelivr.net/npm/mermaid@${MERMAID_VERSION}/dist/mermaid.min.js" integrity="${sri}" crossorigin="anonymous"></script>`,
  local: () => MERMAID_TAG,
}[mermaidMode];
html = html.replace(MERMAID_TAG, mermaidReplacement);

/* 4) 브랜드 데이터 인라인 */
const MARKER = "<!-- build:brand-data -->";
if (!html.includes(MARKER)) fail(`core.html 에서 마커를 찾지 못했습니다: ${MARKER}`);
const json = JSON.stringify(brand).replace(/</g, "\\u003c");
html = html.replace(MARKER, () => `<script type="application/json" id="brand-data">${json}</script>`);

/* 5) 제목 동기화(로드 전 깜빡임 방지) */
if (brand.name) {
  html = html.replace(/<title>.*?<\/title>/, () => `<title>${String(brand.name).replace(/[<>&]/g, "")}</title>`);
}

/* 6) 격리 검사: 다른 브랜드 id 가 산출물에 섞이면 실패
      - web/ 과 --brand-dir 양쪽에 있는 brand.*.json 을 모두 검사
      - 일반 빌드에 PwC 흔적이 남는 사고 방지 */
const brandIds = new Set();
for (const dir of new Set([ROOT, brandDir])) {
  for (const file of fs.readdirSync(dir)) {
    const m = file.match(/^brand\.([a-z0-9-]+)\.json$/i);
    if (m) brandIds.add(m[1].toLowerCase());
  }
}
for (const otherId of brandIds) {
  if (otherId === brandId.toLowerCase()) continue;
  if (new RegExp(otherId, "i").test(html)) {
    fail(`산출물에 다른 브랜드(${otherId}) 흔적이 있습니다. core.html·theme.css·${brandFileRel} 를 확인하세요.`);
  }
}
/* 일반 빌드 시 web/ 안에 PwC 오버레이가 실수로 들어온 경우도 차단 */
if (brandId === "default") {
  for (const leak of ["brand.pwc.json", "theme.pwc.css", "assets/pwc-logo.jpg"]) {
    if (fs.existsSync(path.join(ROOT, leak))) {
      fail(`일반 패키지(web/)에 ${leak} 가 있습니다. internal/pwc/ 로 옮기세요.`);
    }
  }
}

fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, html);
const kb = (fs.statSync(outFile).size / 1024).toFixed(0);
console.log(`✔ ${path.relative(ROOT, outFile)}  (${kb} KB, brand=${brandId}, mermaid=${mermaidMode})`);
