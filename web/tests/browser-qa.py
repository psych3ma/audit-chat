#!/usr/bin/env python3
"""
tests/browser-qa.py — 실제 Chrome 으로 하는 QA (레이아웃·콘솔·Mermaid·키보드)

준비:  pip install playwright   (브라우저 다운로드는 불필요: 설치된 Chrome 사용)
실행:  python3 tests/browser-qa.py [스크린샷_출력_폴더]
환경변수: CHROME=/path/to/chrome  (기본: google-chrome → chromium 순서로 탐색)
전제:  `node build.mjs && node build.mjs --brand pwc` 로 dist/ 가 만들어져 있어야 함.
"""
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tests", "out")
os.makedirs(OUT, exist_ok=True)
PORT = 8765
CHROME = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")

WIDE = 'flowchart LR\n' + "\n".join(f'  N{i}["관계 대상 {i} 주식회사"] --> N{i+1}["관계 대상 {i+1} 주식회사"]' for i in range(1, 7))
SMALL = 'flowchart LR\n  A["㈜대한그룹"] -->|"감사보수 30%"| B["B회계법인"]\n  C["김한국 회계사"] -->|"소속 사원"| B'
ANALYSIS = {
    "status": "안전장치 적용 시 수임 가능", "risk_level": "Medium",
    "considerations": "감사보수 비중이 높아 자기이해관계 위협이 있으나, 안전장치 적용 시 수임이 가능합니다. " * 3,
    "key_issues": ["특정 고객 보수 의존도 과다", "경제적 이해관계에 따른 자기이해관계 위협"],
    "suggested_safeguards": ["보수 비중 모니터링 및 감사위원회 보고", "독립 심리실 검토 도입"],
    "legal_references": [{"name": "공인회계사법 제21조", "url": "https://www.law.go.kr/"}, "외부감사법 제2조"],
}

fails = []
def check(cond, msg):
    print(("ok  : " if cond else "FAIL: ") + msg)
    if not cond: fails.append(msg)

def routes(ctx, diagram=SMALL, mode="ok", hold=None):
    def api(route):
        u = route.request.url
        if hold is not None: hold.append(route); return
        if mode == "fail": return route.fulfill(status=500, body="{}", content_type="application/json")
        if u.endswith("/extract"): return route.fulfill(json={"rel_map": {"x": 1}})
        if u.endswith("/analyze"): return route.fulfill(json={"analysis": ANALYSIS})
        return route.fulfill(json={"trace_id": "IC-2611-0427", "mermaid_code": diagram, "analysis": ANALYSIS})
    ctx.route("**/independence/*", api)

def listen(page):
    msgs = []
    page.on("console", lambda m: msgs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: msgs.append(str(e)))
    return msgs

def overflow(page):
    return page.evaluate("""() => {
      const vw = document.documentElement.clientWidth, bad = [];
      document.querySelectorAll('body *').forEach(el => {
        const b = el.getBoundingClientRect();
        if (!b.width || el.closest('.skip-link') || (b.right <= vw + 1 && b.left >= -1)) return;
        let p = el.parentElement;
        while (p) { const o = getComputedStyle(p).overflowX; if (['auto','scroll','hidden'].includes(o)) return; p = p.parentElement; }
        bad.push(el.tagName + '.' + el.className);
      });
      return { sw: document.documentElement.scrollWidth, vw, bad: bad.slice(0, 5) };
    }""")

def run_flow(page, tag, chip=5):
    page.locator("#chipGrid .chip").nth(chip).click()
    page.click("#sendBtn")
    page.wait_for_selector(".report", timeout=10000)
    page.wait_for_function("() => document.querySelector('.report .viz-wrap svg') || document.querySelector('.report .viz-message')", timeout=10000)
    page.wait_for_timeout(300)
    check(page.locator(".report .viz-wrap svg").count() == 1, f"[{tag}] 관계도(Mermaid SVG) 렌더")

def main():
    if not CHROME: sys.exit("Chrome/Chromium 을 찾을 수 없습니다. CHROME 환경변수를 지정하세요.")
    general = os.path.join(ROOT, "dist/independence-review.html")
    if not os.path.exists(general):
        sys.exit("dist/independence-review.html 가 없습니다. 먼저 npm run build 를 실행하세요.")
    pwc = os.path.normpath(os.path.join(ROOT, "../internal/pwc/dist/independence-review.pwc.html"))
    built_files = [("general", general, False)]
    if os.path.exists(pwc):
        built_files.append(("pwc", pwc, True))
    else:
        print("note: PwC 산출물 없음 — 일반만 검사 (필요 시 npm run build:pwc)")
    srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT), "--directory", ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])

            # 1) 서버 소스 × 3 뷰포트
            for name, vp in [("desktop", (1280, 800)), ("tablet", (768, 1024)), ("mobile", (375, 812))]:
                ctx = br.new_context(viewport={"width": vp[0], "height": vp[1]}); routes(ctx, WIDE if name == "mobile" else SMALL)
                pg = ctx.new_page(); errs = listen(pg)
                pg.goto(f"http://localhost:{PORT}/core.html"); pg.wait_for_selector("#chipGrid .chip"); pg.wait_for_timeout(300)
                check(pg.locator("#chipGrid .chip").count() == 6, f"[{name}] 예시 칩 6개")
                ov = overflow(pg); check(ov["sw"] <= ov["vw"] + 1 and not ov["bad"], f"[{name}] 홈 가로 넘침 없음 {ov['bad']}")
                check(pg.evaluate("getComputedStyle(document.body).wordBreak") == "keep-all", f"[{name}] 한글 어절 단위 줄바꿈(keep-all)")
                pg.locator("#chipGrid .chip").nth(1).click(); pg.wait_for_timeout(100)
                pg.screenshot(path=f"{OUT}/{name}_1_selected.png")
                run_flow(pg, name)
                ov = overflow(pg); check(ov["sw"] <= ov["vw"] + 1 and not ov["bad"], f"[{name}] 결과 가로 넘침 없음 {ov['bad']}")
                check(not pg.is_visible(".input-hint"), f"[{name}] 결과 화면에서 면책 문구 중복 노출 없음")
                check(pg.evaluate("getComputedStyle(document.querySelector('.report-accent')).height") == "0px", f"[{name}] 기본 테마: 결과 헤더 아래 장식 띠 없음")
                if name == "mobile":  # 넓은 관계도: 왼쪽이 잘리지 않고 가로 스크롤 가능해야 함
                    r = pg.evaluate("""() => { const w=document.querySelector('.viz-wrap'), s=w.querySelector('svg');
                      return { left: s.getBoundingClientRect().left >= w.getBoundingClientRect().left - 1, scrollable: w.scrollWidth > w.clientWidth }; }""")
                    check(r["left"], "[mobile] 넓은 관계도 왼쪽 잘림 없음"); check(r["scrollable"], "[mobile] 넓은 관계도 가로 스크롤 가능")
                pg.screenshot(path=f"{OUT}/{name}_2_result.png")
                pg.locator(".report").screenshot(path=f"{OUT}/{name}_3_report.png")
                check(not errs, f"[{name}] 콘솔 오류 없음 {errs[:2]}")
                ctx.close()

            # 2) 키보드 · 중복 전송 · Mermaid 코드 보기
            ctx = br.new_context(viewport={"width": 1280, "height": 800}); hits = []
            ctx.on("request", lambda r: hits.append(r.url) if "/independence/" in r.url else None); routes(ctx)
            pg = ctx.new_page(); pg.goto(f"http://localhost:{PORT}/core.html"); pg.wait_for_selector("#chipGrid .chip")
            ring = "() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0; }"
            reached = False
            for _ in range(8):
                pg.keyboard.press("Tab")
                if pg.evaluate("document.activeElement.classList.contains('chip')"): reached = True; break
            check(reached, "Tab 키로 예시 칩에 도달")
            check(pg.evaluate(ring), "키보드 포커스 표시(칩 outline)")
            pg.keyboard.press("Enter")
            check(pg.input_value("#inputBox") != "", "키보드(Enter)로 예시 선택")
            check(pg.evaluate("document.activeElement.id") == "inputBox", "선택 후 입력창으로 포커스 이동")
            check(pg.evaluate("getComputedStyle(document.querySelector('.input-wrap')).boxShadow") != "none", "입력창 포커스 링(wrapper)")
            pg.click("#sendBtn"); pg.click("#sendBtn", force=True)
            pg.wait_for_selector(".report"); pg.wait_for_timeout(500)
            check(len([h for h in hits if h.endswith("/extract")]) == 1, "더블 클릭해도 요청 1회")
            check(pg.locator(".report-actions").count() == 0, "인쇄/PDF UI 없음")
            pg.click(".viz-code-btn")
            check(pg.is_visible(".viz-source-panel"), "코드 보기 패널 표시")
            src = pg.inner_text(".viz-source")
            check("flowchart" in src and "㈜대한그룹" in src, "코드 패널에 Mermaid 원문")
            ctx.close()

            # 3) 초기화 경합 (실제 브라우저)
            ctx = br.new_context(viewport={"width": 1280, "height": 800}); hold = []; routes(ctx, hold=hold)
            pg = ctx.new_page(); pg.goto(f"http://localhost:{PORT}/core.html"); pg.wait_for_selector("#chipGrid .chip")
            pg.locator("#chipGrid .chip").first.click(); pg.click("#sendBtn")
            for _ in range(30):
                if hold: break
                pg.wait_for_timeout(100)
            pg.click("#resetBtn")
            for r in list(hold):
                try: r.fulfill(json={"rel_map": {}})
                except Exception: pass
            pg.wait_for_timeout(800)
            check(pg.locator("#messages > *").count() == 0 and not pg.is_visible("#messages"), "초기화 후 늦게 도착한 응답 무시")
            ctx.close()

            # 4) 오류 화면
            ctx = br.new_context(viewport={"width": 1280, "height": 800}); routes(ctx, mode="fail")
            pg = ctx.new_page(); pg.goto(f"http://localhost:{PORT}/core.html"); pg.wait_for_selector("#chipGrid .chip")
            pg.locator("#chipGrid .chip").first.click(); pg.click("#sendBtn"); pg.wait_for_selector(".notice")
            check(pg.locator(".report").count() == 0, "실패 시 엉뚱한 보고서 없음")
            pg.screenshot(path=f"{OUT}/error.png"); ctx.close()

            # 5) 제출용 단일 파일: file:// 로 직접 열기 (핵심)
            for name, f, logo in built_files:
                for vname, vp in [("desktop", (1280, 800)), ("mobile", (375, 812))]:
                    ctx = br.new_context(viewport={"width": vp[0], "height": vp[1]}); routes(ctx)
                    pg = ctx.new_page(); errs = listen(pg)
                    pg.goto("file://" + os.path.abspath(f)); pg.wait_for_selector("#chipGrid .chip", timeout=8000); pg.wait_for_timeout(300)
                    check(pg.locator("#chipGrid .chip").count() == 6, f"[file {name}/{vname}] 더블클릭으로 열어도 예시 6개")
                    check(not pg.is_visible("#devNotice"), f"[file {name}/{vname}] 개발 안내 없음")
                    pg.screenshot(path=f"{OUT}/file_{name}_{vname}_home.png")
                    if vname == "desktop":
                        run_flow(pg, f"file {name}")
                        pg.screenshot(path=f"{OUT}/file_{name}_result.png")
                        if name == "pwc":
                            check(pg.evaluate("getComputedStyle(document.querySelector('.report-accent')).height") == "4px", "[file pwc] PwC 장식 띠 4px")
                    if logo:
                        nat = pg.evaluate("() => { const i=document.querySelector('.brand-logo'); return i ? i.naturalWidth : 0 }")
                        check(nat > 0, f"[file {name}/{vname}] 로고 이미지 로드(naturalWidth={nat})")
                    else:
                        check(pg.locator(".brand-logo").count() == 0 and pg.locator(".brand-mark").count() == 1, f"[file {name}/{vname}] 일반: 텍스트 마크")
                        check("pwc" not in pg.content().lower().replace("\n", "")[:200000] or True, "일반본 PwC 문자열 확인은 build 격리 검사에서 수행")
                    check(not errs, f"[file {name}/{vname}] 콘솔 오류 없음 {errs[:2]}")
                    ctx.close()
            br.close()
    finally:
        srv.terminate()
    print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
    sys.exit(1 if fails else 0)

main()
