#!/usr/bin/env python3
"""tests/contrast.py — 토큰 대비율(WCAG AA)과 토큰 일관성 검사. 사용: python3 tests/contrast.py"""
import re, sys, glob, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
p = lambda *a: os.path.join(ROOT, *a)

def parse(path):
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", open(path, encoding="utf-8").read()))

def lum(h):
    h = h.lstrip("#"); v = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    v = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]

def cr(a, b):
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)

def get(t, k):
    v = t[k].strip(); m = re.match(r"var\((--[\w-]+)\)", v)
    return get(t, m.group(1)) if m else v

PAIRS = [
    ("버튼 글자", "--color-on-brand", "--color-brand", 4.5),
    ("본문/배경", "--color-text", "--color-bg", 4.5),
    ("본문/카드", "--color-text", "--color-surface", 4.5),
    ("보조글자/배경", "--color-text-muted", "--color-bg", 4.5),
    ("보조글자/카드", "--color-text-muted", "--color-surface", 4.5),
    ("보조글자/subtle", "--color-text-muted", "--color-subtle", 4.5),
    ("accent/카드", "--color-accent", "--color-surface", 4.5),
    ("accent/배경", "--color-accent", "--color-bg", 4.5),
    ("accent/subtle", "--color-accent", "--color-subtle", 4.5),
    ("브랜드/배경", "--color-brand", "--color-bg", 4.5),
    ("위험 칩", "--on-status-danger", "--status-danger", 4.5),
    ("주의 칩", "--on-status-warn", "--status-warn", 4.5),
    ("가능 칩", "--on-status-ok", "--status-ok", 4.5),
    ("중립 칩", "--on-status-neutral", "--status-neutral", 4.5),
    ("오류 박스", "--status-danger", "--status-danger-soft", 4.5),
    ("안내 박스(주의)", "--status-warn", "--status-warn-soft", 4.5),
    ("사용자 말풍선", "--color-bubble-user-text", "--color-bubble-user-bg", 4.5),
    ("컨트롤 경계/카드", "--color-border-control", "--color-surface", 3.0),
    ("컨트롤 경계/배경", "--color-border-control", "--color-bg", 3.0),
    ("포커스/카드", "--color-focus", "--color-surface", 3.0),
    ("전송 비활성", "--color-text-muted", "--color-border", 4.5),
]

base = parse(p("theme.css"))
themes = {"기본(theme.css)": base}
for f in sorted(glob.glob(p("theme.*.css"))):
    themes[os.path.basename(f)] = {**base, **parse(f)}

bad = 0
for name, t in themes.items():
    print("==", name)
    for label, fg, bg, need in PAIRS:
        r = cr(get(t, fg), get(t, bg)); ok = r >= need; bad += 0 if ok else 1
        print(f"  {'OK ' if ok else 'BAD'} {label:16s} {r:5.2f}:1 (기준 {need})")

core = re.sub(r"<!--.*?-->", "", open(p("core.html"), encoding="utf-8").read(), flags=re.S)
style = re.search(r"<style>(.*?)</style>", core, re.S).group(1)
script = re.findall(r"<script>(.*?)</script>", core, re.S)[-1]
lits = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", style) + re.findall(r"#[0-9a-fA-F]{6}\b", script)
used = set(re.findall(r"var\((--[\w-]+)", style)) | set(re.findall(r'cssVar\("(--[\w-]+)"', script))
local = {"--status-bg", "--status-on"}
undefined = sorted(u for u in used if u not in base and u not in local)
print("\ncore 색상 리터럴:", lits or "없음")
print("theme.css 에 없는 토큰 사용:", undefined or "없음")
print("innerHTML 실사용:", len(re.findall(r"\.innerHTML\s*=|innerHTML\s*\(", script)))
fail = bad + len(lits) + len(undefined)
print("\n결과:", "PASS" if fail == 0 else f"FAIL ({fail})")
sys.exit(1 if fail else 0)
