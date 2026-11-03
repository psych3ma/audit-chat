/**
 * tests/smoke.cjs — jsdom 기반 동작 테스트 (브라우저 없이 빠르게)
 * 실행: npm install && npm test
 * 레이아웃·Mermaid 렌더는 jsdom 으로 검증할 수 없으므로 tests/browser-qa.py 로 확인한다.
 */
const { JSDOM } = require("jsdom");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.join(__dirname, "..");
const stripMermaid = (html) => html.replace(/<script src="vendor\/mermaid\.min\.js"><\/script>/, "");
const sourceHtml = stripMermaid(fs.readFileSync(path.join(ROOT, "core.html"), "utf8"));

// 단일 파일 빌드(내장 brand-data) 경로 검증용: Mermaid 는 local 모드로 두고 태그를 제거
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ir-"));
const builtPath = path.join(tmp, "built.html");
execFileSync("node", [path.join(ROOT, "build.mjs"), "--mermaid", "local", "--out", builtPath], { stdio: "pipe" });
const builtHtml = stripMermaid(fs.readFileSync(builtPath, "utf8"));

let failures = 0;
const ok = (cond, msg) => {
  if (!cond) { failures++; console.log("FAIL:", msg); } else console.log("ok  :", msg);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const REPORT = {
  trace_id: "T1", mermaid_code: "",
  analysis: {
    status: "안전장치 적용 시 수임 가능", risk_level: "Medium",
    considerations: "<img src=x onerror=alert(1)>결론",
    key_issues: ["이슈1"], suggested_safeguards: ["안전장치1"],
    legal_references: [{ name: "법령A", url: "https://law.go.kr/x" }, { name: "나쁜링크", url: "javascript:alert(1)" }],
  },
};

async function boot({ html = sourceHtml, url, mode = {}, brandFetch = true }) {
  const calls = [];
  const pending = [];
  const dom = new JSDOM(html, {
    url, runScripts: "dangerously", pretendToBeVisual: true,
    beforeParse(w) {
      w.HTMLElement.prototype.scrollIntoView = () => {};
      w.print = () => w.dispatchEvent(new w.Event("afterprint"));
      w.fetch = async (u, opt) => {
        const p = String(u);
        if (mode.cloneError && opt && opt.signal) { const e = new Error("AbortSignal object could not be cloned."); e.name = "DataCloneError"; throw e; }
        if (/brand(\.[\w-]+)?\.json$/.test(p)) {
          if (!brandFetch) throw new TypeError("Failed to fetch");
          return { ok: true, status: 200, json: async () => JSON.parse(fs.readFileSync(path.join(ROOT, p.split("/").pop()), "utf8")) };
        }
        calls.push(p);
        if (mode.hold) await new Promise((r) => pending.push(r)); // 응답 지연(초기화 경합 테스트)
        if (mode.fail) return { ok: false, status: mode.fail, json: async () => ({}) };
        if (mode.badJson) return { ok: true, status: 200, json: async () => { throw new SyntaxError("bad"); } };
        if (p.endsWith("/extract")) return { ok: true, status: 200, json: async () => ({ rel_map: { a: 1 } }) };
        if (p.endsWith("/analyze")) return { ok: true, status: 200, json: async () => ({ analysis: { x: 1 } }) };
        return { ok: true, status: 200, json: async () => REPORT };
      };
    },
  });
  const w = dom.window;
  const errs = [];
  w.addEventListener("error", (e) => errs.push(e.message));
  // jsdom 은 stylesheet load 이벤트를 보내지 않으므로 테마 로드 상한(5s)을 넘기지 않도록 대기
  await sleep(mode.wait || 300);
  return { w, d: w.document, calls, errs, release: () => pending.splice(0).forEach((r) => r()) };
}

(async () => {
  /* 1. 소스 + 성공 흐름 */
  let { w, d, calls, errs } = await boot({ url: "http://localhost/core.html" });
  ok(d.body.dataset.state === "ready", "초기화 완료");
  ok(d.querySelectorAll("#chipGrid .chip").length === 6, "예시 칩 6개");
  ok(d.querySelector(".chip-skeleton") === null, "스켈레톤 제거");
  ok(d.getElementById("devNotice").hidden, "정상 로드 시 개발 안내 숨김");
  ok(!/PwC|삼일/.test(d.body.textContent), "일반 브랜드에 타 브랜드 문구 없음");
  ok(d.getElementById("inputBox").placeholder === "예시 시나리오를 선택하세요", "칩 모드 placeholder 문구");
  d.querySelector(".chip").click();
  ok(d.querySelector(".chip").getAttribute("aria-pressed") === "true", "선택된 칩 aria-pressed");

  const box = d.getElementById("inputBox");
  const key = (init) => box.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Enter", bubbles: true, cancelable: true, ...init }));
  key({ isComposing: true }); await sleep(30);
  ok(d.querySelectorAll(".bubble-user").length === 0, "IME 조합 중 Enter 무시");
  key({ keyCode: 229 }); await sleep(30);
  ok(d.querySelectorAll(".bubble-user").length === 0, "keyCode 229 무시");
  key({}); await sleep(30);
  d.getElementById("sendBtn").click(); // 더블 전송 시도
  await sleep(300);
  ok(d.querySelectorAll(".bubble-user").length === 1, "Enter 전송 1회(중복 전송 차단)");
  ok(calls.length === 3, "API 3회 호출: " + calls.join(","));
  const card = d.querySelector(".report");
  ok(!!card && card.dataset.status === "warn", "결과 카드 + warn 톤");
  ok(card.querySelector("img") === null, "응답 HTML 은 텍스트로만 렌더");
  const links = [...card.querySelectorAll("a.law-link")];
  ok(links.length === 1 && links[0].rel.includes("noopener"), "javascript: 링크 차단");
  ok(card.querySelector(".risk") && card.querySelector(".risk").textContent === "(위험도: Medium)", "위험도 문구 nowrap 단위");
  ok(d.body.classList.contains("has-conversation"), "대화 중 입력창 안내 숨김 클래스");
  ok(d.querySelectorAll(".post-chips .chip").length === 6, "하단 시나리오 칩");
  ok(!d.body.textContent.includes("여신") && !d.body.textContent.includes("통제 미흡"), "은행 폴백 문구 없음");
  card.querySelector(".report-actions .btn").click(); await sleep(20);
  ok(!d.body.classList.contains("print-mode"), "인쇄 후 print-mode 정리");
  d.getElementById("resetBtn").click();
  ok(d.getElementById("messages").hidden && !d.getElementById("emptyState").hidden, "초기화 → 홈");
  ok(!d.body.classList.contains("has-conversation"), "초기화 → 입력창 안내 복원");
  ok(errs.length === 0, "런타임 에러 없음 " + errs.join("|"));

  /* 2. 오류 유형별 문구 + 재시도 */
  for (const [mode, expect] of [[{ fail: 404 }, "찾을 수 없습니다"], [{ fail: 500 }, "서버에서 오류"], [{ fail: 429 }, "요청이 많아"], [{ badJson: true }, "응답 형식"]]) {
    ({ d, calls } = await boot({ url: "http://localhost/core.html", mode }));
    d.querySelector(".chip").click(); d.getElementById("sendBtn").click(); await sleep(300);
    const n = d.querySelector(".notice");
    ok(!!n && n.textContent.includes(expect), `오류 문구(${JSON.stringify(mode)}) → "${expect}"`);
    ok(!/localhost|run\.sh|8001/.test(n ? n.textContent : ""), "사용자 문구에 개발 안내 없음");
    ok(!d.querySelector(".report"), "실패 시 보고서 없음");
  }
  ({ d, calls } = await boot({ url: "http://localhost/core.html", mode: { fail: 500 } }));
  d.querySelector(".chip").click(); d.getElementById("sendBtn").click(); await sleep(300);
  const before = calls.length;
  d.querySelector(".notice button").click(); await sleep(300);
  ok(calls.length > before && d.querySelectorAll(".bubble-user").length === 1, "다시 시도 → 재호출, 말풍선 중복 없음");

  /* 3. 초기화 경합: 응답 대기 중 '새 검토 시작' → 이전 응답이 나중에 나타나면 안 됨 */
  let ctx = await boot({ url: "http://localhost/core.html", mode: { hold: true } });
  ctx.d.querySelector(".chip").click(); ctx.d.getElementById("sendBtn").click(); await sleep(100);
  ctx.d.getElementById("resetBtn").click();
  ctx.release(); await sleep(400);
  ok(ctx.d.getElementById("messages").children.length === 0 && ctx.d.getElementById("messages").hidden, "초기화 후 늦게 도착한 응답 무시");
  ok(!ctx.d.getElementById("sendBtn").disabled || ctx.d.getElementById("inputBox").value === "", "초기화 후 전송 상태 정상");

  /* 4. brand.json 로드 실패(file:// 등) → 안내 + 직접 입력 모드 */
  ctx = await boot({ url: "http://localhost/core.html", brandFetch: false });
  ok(ctx.d.body.dataset.state === "ready", "brand.json 실패에도 초기화 완료");
  ok(!ctx.d.getElementById("devNotice").hidden, "개발 안내 표시");
  ok(ctx.d.getElementById("inputBox").readOnly === false, "예시 없음 → 직접 입력 모드");
  ok(ctx.d.getElementById("modeToggle").hidden, "예시 없음 → 모드 토글 숨김");

  /* 5. 단일 파일 빌드(내장 brand-data): fetch 없이 동작 */
  ctx = await boot({ html: builtHtml, url: "http://localhost/built.html", brandFetch: false });
  ok(ctx.d.querySelectorAll("#chipGrid .chip").length === 6, "내장 brand-data 로 칩 6개(파일 fetch 불필요)");
  ok(ctx.d.getElementById("devNotice").hidden, "내장 모드에서는 개발 안내 없음");

  /* 6. PwC 는 web/ 밖(internal/pwc)에서만 빌드 — 내장 brand-data 산출물로 검증 */
  const pwcOut = path.join(tmp, "pwc.html");
  const brandDir = path.join(ROOT, "../internal/pwc");
  if (fs.existsSync(path.join(brandDir, "brand.pwc.json"))) {
    execFileSync(
      "node",
      [path.join(ROOT, "build.mjs"), "--brand", "pwc", "--brand-dir", brandDir, "--mermaid", "local", "--out", pwcOut],
      { stdio: "pipe" },
    );
    const pwcHtml = stripMermaid(fs.readFileSync(pwcOut, "utf8"));
    ctx = await boot({ html: pwcHtml, url: "http://localhost/pwc.html", brandFetch: false });
    ok(ctx.d.title.includes("삼일PwC"), "PwC 타이틀(내장 빌드)");
    ok(ctx.d.getElementById("poweredBy").textContent === "Powered by Samil", "PwC poweredBy");
    ok(ctx.d.querySelectorAll("#chipGrid .chip").length === 6, "PwC 시나리오 6개");
    ok(/theme\.pwc\.css|삼일PwC|--color-brand:\s*#ad1b02/.test(pwcHtml), "PwC 테마 토큰 인라인");
    ok(!fs.existsSync(path.join(ROOT, "brand.pwc.json")), "web/ 에 brand.pwc.json 없음(유출 방지)");
  } else {
    console.log("skip: internal/pwc/brand.pwc.json 없음 — PwC 빌드 테스트 생략");
  }
  ctx = await boot({ url: "http://localhost/core.html?brand=../etc/passwd" });
  ok(ctx.d.title === "감사 독립성 검토 AI", "잘못된 ?brand 값은 기본 brand.json 사용");

  /* 7. ?api 제한 */
  ctx = await boot({ url: "http://localhost/core.html?api=https://evil.example.com" });
  ctx.d.querySelector(".chip").click(); ctx.d.getElementById("sendBtn").click(); await sleep(300);
  ok(ctx.calls[0] && ctx.calls[0].startsWith("/independence"), "허용 외 ?api 무시");
  ctx = await boot({ url: "http://localhost/core.html?api=http://localhost:8001" });
  ctx.d.querySelector(".chip").click(); ctx.d.getElementById("sendBtn").click(); await sleep(300);
  ok(ctx.calls[0] && ctx.calls[0].startsWith("http://localhost:8001/independence"), "localhost ?api 허용");

  /* 8. 미리보기 환경: AbortSignal 복제 불가(DataCloneError) → signal 없이 재시도하여 정상 동작 */
  ctx = await boot({ url: "http://localhost/core.html", mode: { cloneError: true } });
  ok(ctx.d.querySelectorAll("#chipGrid .chip").length === 6 && ctx.d.getElementById("devNotice").hidden, "DataCloneError 환경에서도 brand.json 로드");
  ctx.d.querySelector(".chip").click(); ctx.d.getElementById("sendBtn").click(); await sleep(400);
  ok(!!ctx.d.querySelector(".report") && ctx.calls.length === 3, "DataCloneError 환경에서도 검토 3단계 정상");

  console.log(failures ? `\n${failures} FAILED` : "\nALL PASSED");
  process.exit(failures ? 1 : 0);
})();
